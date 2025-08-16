import json
import re

def convert_json_book_to_txt(json_file_path, output_file_path):
    """Convert JSON book format to simple TXT with HTML headers"""
    
    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract book details
    details = data.get('details', {})
    book_title = details.get('ListBooks_Name', 'Unknown Title')
    author = details.get('ListBooks_Author', 'Unknown Author')
    category = details.get('ListBooks_Category', '')
    
    # Start building the text content
    txt_content = []
    
    # Add main title
    txt_content.append(f"<h1>{book_title}</h1>\n")
    
    # Add author without tags
    if author:
        txt_content.append(f"{author}\n")
    
    # Process the main content
    contain = data.get('contain', {})
    
    # Define Torah book order to preserve traditional sequence
    torah_order = ['בראשית', 'שמות', 'ויקרא', 'במדבר', 'דברים']
    
    # First add books in Torah order if they exist
    processed_keys = set()
    for book_name in torah_order:
        if book_name in contain:
            key = book_name
            processed_keys.add(key)
        else:
            # Try to find the key that contains this book name
            for json_key in contain.keys():
                if book_name in json_key:
                    key = json_key
                    processed_keys.add(key)
                    break
            else:
                continue
        
        section = contain[key]
        
        # Add section header
        if key.strip():
            txt_content.append(f"<h2>{key}</h2>\n\n")
        
        # Process section content
        if isinstance(section, dict):
            # Preserve original subsection order
            subsection_keys = section.keys()
            
            for subkey in subsection_keys:
                subsection = section[subkey]
                
                # Add subsection header
                if subkey.strip():
                    txt_content.append(f"<h3>{subkey}</h3>\n\n")
                
                # Process subsection content
                if isinstance(subsection, dict):
                    for subsubkey, content in subsection.items():
                        if subsubkey.strip():
                            txt_content.append(f"<h4>{subsubkey}</h4>\n\n")
                        
                        # Add the actual text content
                        if isinstance(content, str):
                            # Clean up the text and replace div and br tags with newlines
                            clean_content = re.sub(r'</?div[^>]*>', '\n', content)
                            clean_content = re.sub(r'<br ?/?>', '\n', clean_content)
                            # Remove reference patterns like {$text| [ref] = 'reference'$} and keep only the text
                            clean_content = re.sub(r'\{\$([^}]*?)\|[^}]*\$\}', r'\1', clean_content)
                            # Also handle patterns without pipe: {$text$}
                            clean_content = re.sub(r'\{\$([^}]*?)\$\}', r'\1', clean_content)
                            # Handle incomplete patterns missing {$: text| [ref] = 'reference'$}
                            clean_content = re.sub(r'([^{}\s]+)\|\s*\[ref\][^}]*\$\}', r'\1', clean_content)
                            # Handle incomplete patterns with just [ref] = 'reference'$}
                            clean_content = re.sub(r'\[ref\]\s*=\s*[^}]*\$\}', '', clean_content)
                            # Handle patterns like 'reference'$} or "reference"$}
                            clean_content = re.sub(r"'[^']*'\$\}", '', clean_content)
                            clean_content = re.sub(r'"[^"]*"\$\}', '', clean_content)
                            # Handle patterns like (text$ or text$
                            clean_content = re.sub(r'\([^)]*\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                            clean_content = re.sub(r'[א-ת\w]+\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                            # Handle standalone $ characters
                            clean_content = re.sub(r'\$(?!\})', '', clean_content)
                            # Only collapse spaces and tabs, not newlines
                            clean_content = re.sub(r'[ \t]+', ' ', clean_content.strip())
                            if clean_content:
                                txt_content.append(f"{clean_content}\n\n")
                        elif isinstance(content, dict):
                            # Handle nested content
                            for nested_key, nested_content in content.items():
                                if nested_key.strip():
                                    txt_content.append(f"<h5>{nested_key}</h5>\n\n")
                                if isinstance(nested_content, str) and nested_content.strip():
                                    clean_content = re.sub(r'</?div[^>]*>', '\n', nested_content)
                                    clean_content = re.sub(r'<br ?/?>', '\n', clean_content)
                                    # Remove reference patterns like {$text| [ref] = 'reference'$} and keep only the text
                                    clean_content = re.sub(r'\{\$([^}]*?)\|[^}]*\$\}', r'\1', clean_content)
                                    # Also handle patterns without pipe: {$text$}
                                    clean_content = re.sub(r'\{\$([^}]*?)\$\}', r'\1', clean_content)
                                    # Handle incomplete patterns missing {$: text| [ref] = 'reference'$}
                                    clean_content = re.sub(r'([^{}\s]+)\|\s*\[ref\][^}]*\$\}', r'\1', clean_content)
                                    # Handle incomplete patterns with just [ref] = 'reference'$}
                                    clean_content = re.sub(r'\[ref\]\s*=\s*[^}]*\$\}', '', clean_content)
                                    # Handle patterns like 'reference'$} or "reference"$}
                                    clean_content = re.sub(r"'[^']*'\$\}", '', clean_content)
                                    clean_content = re.sub(r'"[^"]*"\$\}', '', clean_content)
                                    # Handle patterns like (text$ or text$
                                    clean_content = re.sub(r'\([^)]*\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                                    clean_content = re.sub(r'[א-ת\w]+\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                                    # Handle standalone $ characters
                                    clean_content = re.sub(r'\$(?!\})', '', clean_content)
                                    # Only collapse spaces and tabs, not newlines
                                    clean_content = re.sub(r'[ \t]+', ' ', clean_content.strip())
                                    txt_content.append(f"{clean_content}\n\n")
                
                elif isinstance(subsection, str) and subsection.strip():
                    clean_content = re.sub(r'</?div[^>]*>', '\n', subsection)
                    clean_content = re.sub(r'<br ?/?>', '\n', clean_content)
                    # Remove reference patterns like {$text| [ref] = 'reference'$} and keep only the text
                    clean_content = re.sub(r'\{\$([^}]*?)\|[^}]*\$\}', r'\1', clean_content)
                    # Also handle patterns without pipe: {$text$}
                    clean_content = re.sub(r'\{\$([^}]*?)\$\}', r'\1', clean_content)
                    # Handle incomplete patterns missing {$: text| [ref] = 'reference'$}
                    clean_content = re.sub(r'([^{}\s]+)\|\s*\[ref\][^}]*\$\}', r'\1', clean_content)
                    # Handle incomplete patterns with just [ref] = 'reference'$}
                    clean_content = re.sub(r'\[ref\]\s*=\s*[^}]*\$\}', '', clean_content)
                    # Handle patterns like 'reference'$} or "reference"$}
                    clean_content = re.sub(r"'[^']*'\$\}", '', clean_content)
                    clean_content = re.sub(r'"[^"]*"\$\}', '', clean_content)
                    # Handle patterns like (text$ or text$
                    clean_content = re.sub(r'\([^)]*\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                    clean_content = re.sub(r'[א-ת\w]+\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                    # Handle standalone $ characters
                    clean_content = re.sub(r'\$(?!\})', '', clean_content)
                    # Only collapse spaces and tabs, not newlines
                    clean_content = re.sub(r'[ \t]+', ' ', clean_content.strip())
                    txt_content.append(f"{clean_content}\n\n")
        
        elif isinstance(section, str) and section.strip():
            clean_content = re.sub(r'</?div[^>]*>', '\n', section)
            clean_content = re.sub(r'<br ?/?>', '\n', clean_content)
            # Remove reference patterns like {$text| [ref] = 'reference'$} and keep only the text
            clean_content = re.sub(r'\{\$([^}]*?)\|[^}]*\$\}', r'\1', clean_content)
            # Also handle patterns without pipe: {$text$}
            clean_content = re.sub(r'\{\$([^}]*?)\$\}', r'\1', clean_content)
            # Handle incomplete patterns missing {$: text| [ref] = 'reference'$}
            clean_content = re.sub(r'([^{}\s]+)\|\s*\[ref\][^}]*\$\}', r'\1', clean_content)
            # Handle incomplete patterns with just [ref] = 'reference'$}
            clean_content = re.sub(r'\[ref\]\s*=\s*[^}]*\$\}', '', clean_content)
            # Handle patterns like 'reference'$} or "reference"$}
            clean_content = re.sub(r"'[^']*'\$\}", '', clean_content)
            clean_content = re.sub(r'"[^"]*"\$\}', '', clean_content)
            # Handle patterns like (text$ or text$
            clean_content = re.sub(r'\([^)]*\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
            clean_content = re.sub(r'[א-ת\w]+\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
            # Handle standalone $ characters
            clean_content = re.sub(r'\$(?!\})', '', clean_content)
            # Only collapse spaces and tabs, not newlines
            clean_content = re.sub(r'[ \t]+', ' ', clean_content.strip())
            txt_content.append(f"{clean_content}\n\n")
    
    # Process any remaining keys that weren't in the Torah order
    for key in contain.keys():
        if key not in processed_keys:
            section = contain[key]
            
            # Add section header
            if key.strip():
                txt_content.append(f"<h2>{key}</h2>\n\n")
            
            # Process section content (same logic as above)
            if isinstance(section, dict):
                subsection_keys = section.keys()
                
                for subkey in subsection_keys:
                    subsection = section[subkey]
                    
                    if subkey.strip():
                        txt_content.append(f"<h3>{subkey}</h3>\n\n")
                    
                    if isinstance(subsection, dict):
                        for subsubkey, content in subsection.items():
                            if subsubkey.strip():
                                txt_content.append(f"<h4>{subsubkey}</h4>\n\n")
                            
                            if isinstance(content, str):
                                clean_content = re.sub(r'</?div[^>]*>', '\n', content)
                                clean_content = re.sub(r'<br ?/?>', '\n', clean_content)
                                # Remove reference patterns like {$text| [ref] = 'reference'$} and keep only the text
                                clean_content = re.sub(r'\{\$([^}]*?)\|[^}]*\$\}', r'\1', clean_content)
                                # Also handle patterns without pipe: {$text$}
                                clean_content = re.sub(r'\{\$([^}]*?)\$\}', r'\1', clean_content)
                                # Handle incomplete patterns missing {$: text| [ref] = 'reference'$}
                                clean_content = re.sub(r'([^{}\s]+)\|\s*\[ref\][^}]*\$\}', r'\1', clean_content)
                                # Handle incomplete patterns with just [ref] = 'reference'$}
                                clean_content = re.sub(r'\[ref\]\s*=\s*[^}]*\$\}', '', clean_content)
                                # Handle patterns like 'reference'$} or "reference"$}
                                clean_content = re.sub(r"'[^']*'\$\}", '', clean_content)
                                clean_content = re.sub(r'"[^"]*"\$\}', '', clean_content)
                                # Handle patterns like (text$ or text$
                                clean_content = re.sub(r'\([^)]*\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                                clean_content = re.sub(r'[א-ת\w]+\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                                # Handle standalone $ characters
                                clean_content = re.sub(r'\$(?!\})', '', clean_content)
                                clean_content = re.sub(r'[ \t]+', ' ', clean_content.strip())
                                if clean_content:
                                    txt_content.append(f"{clean_content}\n\n")
                            elif isinstance(content, dict):
                                for nested_key, nested_content in content.items():
                                    if nested_key.strip():
                                        txt_content.append(f"<h5>{nested_key}</h5>\n\n")
                                    if isinstance(nested_content, str) and nested_content.strip():
                                        clean_content = re.sub(r'</?div[^>]*>', '\n', nested_content)
                                        clean_content = re.sub(r'<br ?/?>', '\n', clean_content)
                                        # Remove reference patterns like {$text| [ref] = 'reference'$} and keep only the text
                                        clean_content = re.sub(r'\{\$([^}]*?)\|[^}]*\$\}', r'\1', clean_content)
                                        # Also handle patterns without pipe: {$text$}
                                        clean_content = re.sub(r'\{\$([^}]*?)\$\}', r'\1', clean_content)
                                        # Handle incomplete patterns missing {$: text| [ref] = 'reference'$}
                                        clean_content = re.sub(r'([^{}\s]+)\|\s*\[ref\][^}]*\$\}', r'\1', clean_content)
                                        # Handle incomplete patterns with just [ref] = 'reference'$}
                                        clean_content = re.sub(r'\[ref\]\s*=\s*[^}]*\$\}', '', clean_content)
                                        # Handle patterns like 'reference'$} or "reference"$}
                                        clean_content = re.sub(r"'[^']*'\$\}", '', clean_content)
                                        clean_content = re.sub(r'"[^"]*"\$\}', '', clean_content)
                                        # Handle patterns like (text$ or text$
                                        clean_content = re.sub(r'\([^)]*\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                                        clean_content = re.sub(r'[א-ת\w]+\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                                        # Handle standalone $ characters
                                        clean_content = re.sub(r'\$(?!\})', '', clean_content)
                                        clean_content = re.sub(r'[ \t]+', ' ', clean_content.strip())
                                        txt_content.append(f"{clean_content}\n\n")
                    
                    elif isinstance(subsection, str) and subsection.strip():
                        clean_content = re.sub(r'</?div[^>]*>', '\n', subsection)
                        clean_content = re.sub(r'<br ?/?>', '\n', clean_content)
                        # Remove reference patterns like {$text| [ref] = 'reference'$} and keep only the text
                        clean_content = re.sub(r'\{\$([^}]*?)\|[^}]*\$\}', r'\1', clean_content)
                        # Also handle patterns without pipe: {$text$}
                        clean_content = re.sub(r'\{\$([^}]*?)\$\}', r'\1', clean_content)
                        # Handle incomplete patterns missing {$: text| [ref] = 'reference'$}
                        clean_content = re.sub(r'([^{}\s]+)\|\s*\[ref\][^}]*\$\}', r'\1', clean_content)
                        # Handle incomplete patterns with just [ref] = 'reference'$}
                        clean_content = re.sub(r'\[ref\]\s*=\s*[^}]*\$\}', '', clean_content)
                        # Handle patterns like 'reference'$} or "reference"$}
                        clean_content = re.sub(r"'[^']*'\$\}", '', clean_content)
                        clean_content = re.sub(r'"[^"]*"\$\}', '', clean_content)
                        # Handle patterns like (text$ or text$
                        clean_content = re.sub(r'\([^)]*\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                        clean_content = re.sub(r'[א-ת\w]+\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                        # Handle standalone $ characters
                        clean_content = re.sub(r'\$(?!\})', '', clean_content)
                        clean_content = re.sub(r'[ \t]+', ' ', clean_content.strip())
                        txt_content.append(f"{clean_content}\n\n")
            
            elif isinstance(section, str) and section.strip():
                clean_content = re.sub(r'</?div[^>]*>', '\n', section)
                clean_content = re.sub(r'<br ?/?>', '\n', clean_content)
                # Remove reference patterns like {$text| [ref] = 'reference'$} and keep only the text
                clean_content = re.sub(r'\{\$([^}]*?)\|[^}]*\$\}', r'\1', clean_content)
                # Also handle patterns without pipe: {$text$}
                clean_content = re.sub(r'\{\$([^}]*?)\$\}', r'\1', clean_content)
                # Handle incomplete patterns missing {$: text| [ref] = 'reference'$}
                clean_content = re.sub(r'([^{}\s]+)\|\s*\[ref\][^}]*\$\}', r'\1', clean_content)
                # Handle incomplete patterns with just [ref] = 'reference'$}
                clean_content = re.sub(r'\[ref\]\s*=\s*[^}]*\$\}', '', clean_content)
                # Handle patterns like 'reference'$} or "reference"$}
                clean_content = re.sub(r"'[^']*'\$\}", '', clean_content)
                clean_content = re.sub(r'"[^"]*"\$\}', '', clean_content)
                # Handle patterns like (text$ or text$
                clean_content = re.sub(r'\([^)]*\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                clean_content = re.sub(r'[א-ת\w]+\$(?!\})', lambda m: m.group(0)[:-1], clean_content)
                # Handle standalone $ characters
                clean_content = re.sub(r'\$(?!\})', '', clean_content)
                clean_content = re.sub(r'[ \t]+', ' ', clean_content.strip())
                txt_content.append(f"{clean_content}\n\n")
    
    # Join content and remove empty lines
    full_content = ''.join(txt_content)
    # Remove empty lines (lines with only whitespace)
    lines = full_content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    final_content = '\n'.join(non_empty_lines)
    
    # Write to output file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Conversion completed! Output saved to: {output_file_path}")
    print(f"Book title: {book_title}")
    print(f"Author: {author}")

if __name__ == "__main__":
    import json
    import glob
    import os
    
    # Find all JSON files in the current directory
    json_files = glob.glob("*.json")
    
    if not json_files:
        print("No JSON files found in the directory.")
    else:
        print(f"Found {len(json_files)} JSON file(s) to process:")
        
        for json_file in json_files:
            print(f"\nProcessing: {json_file}")
            
            try:
                # Extract book name from JSON to create output filename
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                book_title = data.get('details', {}).get('ListBooks_Name', f'Unknown_Book_{os.path.splitext(json_file)[0]}')
                # Clean filename - replace problematic characters
                clean_title = book_title.replace('"', '').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('<', '_').replace('>', '_').replace('|', '_').strip()
                output_file = f"{clean_title}.txt"
                
                convert_json_book_to_txt(json_file, output_file)
                
            except Exception as e:
                print(f"Error processing {json_file}: {str(e)}")
                continue
        
        print(f"\nCompleted processing all JSON files!")