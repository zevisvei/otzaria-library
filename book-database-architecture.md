# Book Database Architecture in Otzaria

## 1. Hierarchical Library Structure

```pseudocode
// Basic library structure
class Library {
    List<Category> subCategories
}

// Category structure
class Category {
    String title
    String description
    String shortDescription
    int order
    List<Category> subCategories
    List<Book> books
    Category? parent
}

// Basic book structure
class Book {
    String title
    List<String>? extraTitles
    String? author
    String? heShortDesc
    String? pubDate
    String? pubPlace
    int order
    String topics
    Category? category
}

// Text book with content and table of contents
class TextBook extends Book {
    Future<String> text                // Complete textual content
    Future<List<TocEntry>> tableOfContents  // Table of contents
    Future<List<Link>> links           // Links to other texts
}

// Table of contents entry
class TocEntry {
    String text                // Title text
    int index                  // Position in the book
    int level                  // Hierarchical level (1=chapter, 2=section, etc.)
    TocEntry? parent           // Parent entry
    List<TocEntry> children    // Child entries
}

// Link between two texts
class Link {
    String heRef               // Hebrew reference
    int index1                 // Index in the source book
    String path2               // Path to the target book
    int index2                 // Index in the target book
    String connectionType      // Connection type (commentary, targum, etc.)
}
```

## 2. File System Organization

```pseudocode
// File system structure
LibraryRoot/
  ├── אוצריא/                  // Main directory
  │   ├── Category1/           // Main categories
  │   │   ├── Subcategory1/    // Subcategories
  │   │   │   ├── Book1.txt    // Books in text format
  │   │   │   └── Book2.docx   // Books in docx format
  │   │   └── Book3.pdf        // Books in PDF format
  │   └── Category2/
  │       └── ...
  ├── links/                   // Links directory
  │   ├── Book1_links.json     // Links for each book
  │   └── Book2_links.json
  └── metadata.json            // Metadata for all books
```

## 3. Library Loading

```pseudocode
// Loading the complete library
function getLibrary():
    // Load metadata
    metadata = loadJsonFile("metadata.json")
    
    // Build hierarchical structure
    library = new Library()
    
    // Recursively traverse the main directory
    for each folder in "אוצריא/":
        category = createCategory(folder, metadata)
        library.subCategories.add(category)
    
    // Sort categories by order
    library.subCategories.sort(byOrder)
    
    return library

// Recursive category creation
function createCategory(folder, metadata, parent=null):
    title = extractTitleFromPath(folder.path)
    
    category = new Category(
        title: title,
        description: metadata[title]?.description ?? "",
        shortDescription: metadata[title]?.shortDescription ?? "",
        order: metadata[title]?.order ?? 999,
        parent: parent
    )
    
    // Process subfolders as subcategories
    for each entity in folder:
        if entity is a folder:
            subcategory = createCategory(entity, metadata, category)
            category.subCategories.add(subcategory)
        else if entity is a file:
            // Extract topics from path
            topics = extractTopics(entity.path)
            
            // Process by file type
            if entity.path ends with ".pdf":
                book = createPdfBook(entity, metadata, category, topics)
                category.books.add(book)
            else if entity.path ends with ".txt" or ".docx":
                book = createTextBook(entity, metadata, category, topics)
                category.books.add(book)
    
    // Sort subcategories and books
    category.subCategories.sort(byOrder)
    category.books.sort(byOrder)
    
    return category
```

## 4. Book Content Access

```pseudocode
// Get book text
function getBookText(title):
    path = getBookPath(title)
    
    if path ends with ".docx":
        // Convert DOCX to text
        bytes = readBinaryFile(path)
        return convertDocxToText(bytes)
    else:
        // Read text file directly
        content = readTextFile(path)
        return content

// Get table of contents
function getBookToc(title):
    content = getBookText(title)
    return parseToc(content)

// Parse table of contents
function parseToc(content):
    lines = content.splitByLines()
    toc = []
    parents = {} // Track parent nodes
    
    for i from 0 to lines.length - 1:
        line = lines[i]
        
        if line.startsWith("<h"):
            level = extractLevel(line) // Ex: <h1> = level 1
            text = removeHtmlTags(line)
            
            if level == 1:
                // Add as root node
                entry = new TocEntry(text, i, level)
                toc.add(entry)
                parents[level] = entry
            else:
                // Add under appropriate parent
                parent = parents[level - 1]
                entry = new TocEntry(text, i, level, parent)
                
                if parent exists:
                    parent.children.add(entry)
                    parents[level] = entry
                else:
                    toc.add(entry)
    
    return toc
```

## 5. Commentary Management (פרשנות)

```pseudocode
// Get all links for a book
function getAllLinksForBook(title):
    linksPath = "links/" + title + "_links.json"
    
    try:
        jsonString = readFile(linksPath)
        jsonList = decodeJson(jsonString)
        links = []
        
        for each json in jsonList:
            link = new Link(
                heRef: json["heRef_2"],
                index1: json["line_index_1"],
                path2: json["path_2"],
                index2: json["line_index_2"],
                connectionType: json["Conection Type"]
            )
            links.add(link)
        
        return links
    catch Exception:
        return [] // No links found

// Get available commentators
function getAvailableCommentators(links):
    // Filter commentary links
    commentaryLinks = links.filter(link => 
        link.connectionType == "commentary" || 
        link.connectionType == "targum"
    )
    
    // Extract unique paths
    paths = commentaryLinks.map(link => link.path2)
    uniquePaths = removeDuplicates(paths)
    
    // Convert paths to book titles
    commentatorTitles = uniquePaths.map(path => 
        extractTitleFromPath(path)
    )
    
    // Verify commentator existence
    availableCommentators = []
    for each title in commentatorTitles:
        if bookExists(title):
            availableCommentators.add(title)
    
    // Sort alphabetically
    availableCommentators.sort()
    
    return availableCommentators

// Get links for visible indices
function getLinksForIndices(indices, links, activeCommentators):
    allLinks = []
    
    for each index in indices:
        // Find links matching this index
        indexLinks = links.filter(link => 
            link.index1 == index + 1 && 
            (link.connectionType == "commentary" || link.connectionType == "targum") &&
            activeCommentators.contains(extractTitleFromPath(link.path2))
        )
        
        allLinks.merge(indexLinks)
    
    // Sort by Hebrew reference
    allLinks.sort(byHebrewReference)
    
    // Sort by commentator order
    allLinks.sort(byCommentatorOrder)
    
    return allLinks
```

## 6. Usage Flow

```pseudocode
// Opening a book
function openBook(title):
    // Load book content
    book = new TextBook(title)
    content = await book.text
    
    // Load table of contents
    toc = await book.tableOfContents
    
    // Load links
    links = await book.links
    
    // Determine available commentators
    availableCommentators = await getAvailableCommentators(links)
    
    // Initialize user interface
    displayBookContent(content)
    displayTableOfContents(toc)
    displayAvailableCommentators(availableCommentators)

// Display commentaries
function displayCommentaries(visibleIndices, activeCommentators):
    // Get links for visible indices
    links = await getLinksForIndices(visibleIndices, book.links, activeCommentators)
    
    commentaries = []
    for each link in links:
        // Load commentary content
        commentaryContent = await link.content
        commentary = {
            text: commentaryContent,
            title: extractTitleFromPath(link.path2),
            reference: link.heRef
        }
        commentaries.add(commentary)
    
    // Display commentaries alongside main text
    displayCommentariesNextToText(commentaries)
```

## Summary

1. **Hierarchical data structure**:
   - The library is organized into categories and subcategories
   - Each category can contain books and other subcategories
   - Books can be text (TextBook) or PDF (PdfBook)

2. **File system**:
   - Books are stored in a hierarchical folder structure
   - Metadata is centralized in a JSON file
   - Links between texts are stored in separate JSON files

3. **Table of contents**:
   - Dynamically generated by analyzing HTML tags in the text
   - Hierarchical structure with entries of different levels
   - Each entry contains text, index, and references to parent/child entries

4. **Commentary system**:
   - Commentaries are linked to books via Link objects
   - Each link contains a reference to the source text and the commentary
   - The application filters available commentators for each book
   - The user can select which commentators to display

This architecture enables a rich study experience where users can easily navigate texts, access the table of contents, and consult different interpretations of the same passage.
