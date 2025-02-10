# this script takes the library of sefaria, and converts it to be used in otzaria

import json
import os
from hebrew_numbers import int_to_gematria
output = []

# the code for each level in the hierarchy
codes =[['<h1>','</h1>'],['<h2>','</h2>'],['<h3>','</h3>'],['<h4>','</h4>'],['<h5>','</h5>'],['<h5>','</h5>'],['<h5>','</h5>'],['<h5>','</h5>'],['<h5>','</h5>']]

def to_gematria(i)->str:
    s = ''
    i = i%1000
    j = i/1000
    if j<0:
        s = int_to_gematria(j, gershayim=False)+ ' '
    s = s + int_to_gematria(i, gershayim=False)
    return s
        

def get_content_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content

def to_daf(i)->str:
        i+=1
        if  i%2 ==0:
            return to_gematria(i//2)+'.'
        else: 
            return to_gematria(i//2)+':'
    

def recursive_sections(section_names, text, depth,level=0):
        """
        Recursively generates section names based on depth and appends to output list.
        :param section_names: list of section names
        :param text: input text
        :param depth: current depth of recursion
        :return: None
        """
        if depth == 0 and text != [] and type(text) is not bool:
            globals()['output'].append(text.replace('\n','')+'\n')
        elif type(text) != bool:
            for i, item in enumerate(text, start=1):
                if item != [] and item != [[]]:
                    letter = to_daf(i) if section_names[-depth] == 'דף' else to_gematria(i)
                    if depth>1:                        
                        globals()['output'].append(f"{codes[level][0]}{section_names[-depth]} {letter}{codes[level][1]}\n")
                    elif section_names[-depth] != 'שורה' and section_names[-depth] != 'פירוש' and section_names[-depth] != 'פסקה':
                        globals()['output'].append(f'({letter}) ')

                        
                recursive_sections(section_names, item, depth-1,level+1)
                

def process_node(node, text,level=0):
    """
    Process a given node, handling both nested nodes and nested arrays.
    :param node: the current node being processed
    :param text: the text associated with the node
    :param output: the output list to which the processed text is appended
    :return: None
    """
    if 'nodes' in node:  # Process nested nodes
        node_title = node['heTitle']
        globals()['output'].append(f"{codes[level][0]}{node_title}{codes[level][1]}\n")
        for sub_node in node['nodes']:
            process_node(sub_node, text[sub_node['title']] if sub_node['key']!='default' else text[''],level=level+1)
    else:  # Process nested arrays
        node_title = node['heTitle']
        section_names = node['heSectionNames']
        depth = node.get('depth', 1)
        globals()['output'].append(f"{codes[level][0]}{node_title}{codes[level][1]}\n")
        recursive_sections(section_names, text, depth,level+1)

def process_complex_book(text_file_name, schema_file_name, output_file_name):
    """
    Process a book divided into nodes and generates an output file.
    :param text_file_name: the file name of the book's text
    :param schema_file_name: the file name of the book's schema
    :param output_file_name: the file name for the output
    :return: None
    """
    index = get_content_from_json(file_path=schema_file_name)
    text = get_content_from_json(file_path=text_file_name)
    # add book title
    globals()['output'].append(f'<h1>{index["schema"]["heTitle"]}</h1>\n')
    # add authors name
    if 'authors' in index:
        for author in index['authors']:
            globals()['output'].append(author['he']+'\n')   
    
    for node in index['schema']['nodes']:
        try:
            process_node(node, text['text'][node['title']] if node['key']!='default' else text['text'][''],level=1)
        except KeyError :
            print(text_file_name)
            return

def process_simple_book(text_file_name,schema_file_name,output_file_name):
    index = get_content_from_json(file_path =schema_file_name)
    sectionNames = index['schema']['heSectionNames']
    depth = index['schema']['depth']
    text = get_content_from_json(file_path = text_file_name)
    # add book title
    globals()['output'].append(f'<h1>{index["schema"]["heTitle"]}</h1>\n')
    # add authors name
    if 'authors' in index:
        for author in index['authors']:
            globals()['output'].append(author['he']+'\n')            
    recursive_sections(sectionNames, text['text'], depth,1)

        
        

def process_book(text_file_name, schema_file_name, output_file_name):
    """
    Process a book based on the provided text, schema, and output file names.

    :param text_file_name: The name of the text file containing the book content.
    :param schema_file_name: The name of the schema file for processing the book.
    :param output_file_name: The name of the output file to write the processed book to.
    :return: None
    """
    globals()['output'] = []
    with open("blacklist.txt", 'r', encoding='utf-8') as file:
        blacklist = file.read().splitlines()
    schema = get_content_from_json(file_path=schema_file_name)
    if schema['schema']['title'] in blacklist:
        return
    if 'nodes' in schema['schema']:
        process_complex_book(text_file_name, schema_file_name, output_file_name)
    else:
        process_simple_book(text_file_name, schema_file_name, output_file_name)
    # write the output to the output file in windows-1255 encoding
    with open(output_file_name, 'w', encoding='utf-8') as file:
        file.writelines(output)
        
    


def process_all_books_in_folder(json_folder, schemas_folder,output_folder):
    """
    Process all books in the given folder whose path ends with 'Hebrew/Merged.json'.
    It finds the corresponding schema file in the schemas folder by matching the
    pattern '/xxxx/Hebrew/Merged.json' to 'xxxx.json'.

    :param folder_path: Path to the folder containing the book files.
    :param schemas_folder: Path to the folder containing the schema files.
    """
    with open("blacklist.txt", 'r', encoding='utf-8') as file:
        blacklist = file.read().splitlines()
    for root, _,files in os.walk(json_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if  file_path.endswith('Hebrew\\merged.json') and file_path.split('\\')[-3] not in blacklist:
                text_file = file_path
                title = file_path.split('\\')[-3].replace(' ', '_')
                schema_file_name = os.path.join(schemas_folder, title + '.json')
                categories = get_content_from_json(schema_file_name)["heCategories"]
                output_path = ''
                for category in categories:
                    output_path += category.replace('"','')+'\\'
                os.makedirs(os.path.join(output_folder, output_path),exist_ok=True)
                output_file_name = os.path.join(output_folder, output_path) + get_content_from_json(schema_file_name)['schema']['heTitle'].replace('"','').replace("'",'').replace('״','') + '.txt'
                process_book(text_file, schema_file_name, output_file_name)
            
process_all_books_in_folder("..\\..\\database_export\\json",
                            "..\\..\\database_export\\schemas",
                           "..\\אוצריא")


