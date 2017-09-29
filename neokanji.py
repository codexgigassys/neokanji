from py2neo import Graph
import json
import sys
from os import listdir
from IPython import embed
import argparse
import config 

logo = open("Logo", "r")
log_img = logo.read()
logo.close()
print log_img

cypher_clean_empty_comp = """
    MATCH (a:Compilation_Time{comp_time:"-"})
    DETACH DELETE a
"""

cypher_clean_empty_filename = """
   MATCH (n:File_Name{file_name:'-'})
   DETACH DELETE n
"""

cypher_clean_empty_filetype = """
    MATCH (d:File_Type{type:'-'})
    DETACH DELETE d
    """

cypher_clean_empty_pdb = """
    MATCH (c:pdb{PDB:'-'})
    DETACH DELETE c
"""

cypher_clean_empty_last_saved = """
    MATCH (c:Last_Saved{date:'-'})
    DETACH DELETE c
"""

cypher_link_mw_pdb = """
    MERGE (a:Malware{md5:{md5}})
    MERGE (b:pdb{PDB:{pdb}})
    CREATE (a)-[:HAS_PDB]->(b)
"""

cypher_create_mw_node = """
    MERGE (a:Malware{md5:{md5}, sha1:{sha1}, sha256:{sha256}})
    MERGE (b:Compilation_Time{comp_time:{comp_time}})
    MERGE (c:File_Type{type:{file_type}})
    MERGE (d:File_Name{file_name:{file_name}})
    MERGE (a)-[:dates]-(b)
    MERGE (a)-[:is]-(c)
    MERGE (a)-[:has_name]-(d)
"""

cypher_link_mw_signature = """
    MERGE (a:Signature{description:{description}, severity:{severity}})
    MERGE (b:Malware{md5:{md5}})
    MERGE (b)-[:behaves]->(a)
"""

cypher_add_apt = """
    MERGE (a:APT{name:{name}})
"""

cypher_link_macro_mw = """
    MERGE (a:Malware{md5:{md5}})
    MERGE (b:Macro{macro_name:{macro}})
    MERGE (a)-[:EXECUTES]->(b)
"""

cypher_link_lsaved_mw = """
    MERGE (a:Malware{md5:{md5}})
    MERGE (b:Last_Saved{date:{date}})
    MERGE (a)-[:LAST_SAVED]->(b)
"""

cypher_relate_apt_mw = """
    MERGE (a:Malware{md5:{md5}})
    MERGE (b:APT{name:{name}})
    MERGE (b)-[:uses]-(a)
"""

cypher_link_mw_int = """
    MERGE (a:Malware{md5:{md5}})
    MERGE (b:String{string:{string}})
    MERGE (a)-[:contains]->(b)
"""
# -----------------------------------------------------------------------------


def get_tools_info(folder):
    tools = dict()
    for file in listdir(folder):
        if not file.endswith((".json")):
            continue
        tool_name = file.replace(".json", "")
        file_handler = open(folder + file, 'r')
        json_data = file_handler.read()
        file_handler.close()
        tool_info = json.loads(json_data)
        tools[tool_name] = tool_info
        print tools
    return tools
# -----------------------------------------------------------------------------


NEO4J_PASSWORD = config.password
NEO4J_USER = config.user
NEO4J_PORT = config.port


def add_macro_mw_rel(tx, macro, md5):
    tx.run(cypher_link_macro_mw, {'md5': md5, 'macro': macro})


def add_apt(tx, apt):
    tx.run(cypher_add_apt, {"name": apt})


def add_mw(tx, md5, sha1, sha256, file_type, file_name, comp_time):
    tx.run(cypher_create_mw_node, {"md5": md5,
                                   "sha1": sha1,
                                   "sha256": sha256,
                                   "file_type": file_type,
                                   "file_name": file_name,
                                   "comp_time": comp_time})


def add_apt_mw_rel(tx, apt, md5):
    tx.run(cypher_relate_apt_mw, {"name": apt, "md5": md5})


def add_int_mw_rel(tx, st, md5):
    tx.run(cypher_link_mw_int, {'string': st, 'md5': md5})


def add_mw_signature(tx, signatures, md5):
    for sig in signatures:
        tx.run(cypher_link_mw_signature, {
            "description": sig.get('description'),
            "severity": sig.get('severity'), "md5": md5})


def add_office_last_saved(tx, date, md5):
    tx.run(cypher_link_lsaved_mw, {'date': date, 'md5': md5})


def add_pdb_mw_rel(tx, pdb, md5):
    tx.run(cypher_link_mw_pdb, {'pdb': pdb, 'md5': md5})


def extract_codex_data(folder):
    try:
        for file in listdir(folder):
            if not file.endswith((".txt")):
                continue
            codex_extractor.main(folder + file)

    except Exception as e:
        raise e

class CustomParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    parser = CustomParser()
    parser.add_argument("--input", "-i",
                        help="sets input folder")

    args = parser.parse_args()
    # print args.input


    extract_codex_data(args.input)
    # codex_extractor.main(args)

    graph_http = "http://" + NEO4J_USER + ":" + \
        NEO4J_PASSWORD + "@:" + NEO4J_PORT + "/db/data/"
    GRAPH = Graph(graph_http)

    GRAPH.delete_all()
    with GRAPH.begin() as tx:
        data = get_tools_info(args.input)
        for apt in data:

            add_apt(tx, apt)
            for file in data[apt]:
                add_mw(tx, file['MD5'],
                       file['SHA1'],
                       file['SHA256'],
                       file['Description'],
                       file['File_Name'],
                       file['Compilation_Time']
                       )
                add_apt_mw_rel(tx, apt, file['MD5'])
                for pdb in file['PDB']:
                    add_pdb_mw_rel(tx, pdb, file['MD5'])
                try:
                    add_mw_signature(tx, file['Signatures'], file['MD5'])
                    for st in file['Interesting']:
                        add_int_mw_rel(tx, st, file['MD5'])
                except KeyError:
                    print file['MD5'] + " error"
                    print KeyError.message
                    pass
                try:
                    for macro in file['Office']:
                        add_macro_mw_rel(tx, macro, file['MD5'])
                    add_office_last_saved(tx, file['Last_Saved'], file['MD5'])
                except Exception:
                    pass
        tx.run(cypher_clean_empty_comp)
        tx.run(cypher_clean_empty_filetype)
        tx.run(cypher_clean_empty_filename)
        tx.run(cypher_clean_empty_pdb)
        tx.run(cypher_clean_empty_last_saved)


if __name__ == "__main__":
    main()
