# NeoKanji

NeoKanji is a tool that looks forward to helping researchers with visualization and correlation of threat actors, campaigns, malware samples, signatures and other characteristics in a set of data.

## Getting Started

You need an instance of NEO4J running in your host. The easiest way to set it up is to run the following command:
```bash
docker run \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    --volume=$HOME/neo4j/logs:/logs \
    neo4j:3.0
```

Once set up, browse to http://localhost:7474/browser/ and change your password.
Configure config.py file with your data. 

Place your JSONs files in a folder and then simply run
```bash
python neokanji.py -i <inputfolder>
 ```

Open your Neo4J instance and start playing with data. I strongly recommend to read [Cyber Query Language Introduction](https://neo4j.com/developer/cypher-query-language/) to improve queries performance and finding interesting items. 


### Prerequisites
Libraries needed:
* py2neo

[Docker](https://www.docker.com/) is needed and strongly recommended.


### Input Format
Neokanji should be feed with JSON files describing behavior and/or attributes.

__data **must be** provided by yourself__.

The input JSON file should look like this:

```json
{
   "SHA1":"c380038a57ffb8c064851b898f630312fabcbba7",
   "Interesting":[
      "'%s.dll'",
      "'d$(.dll'",
      "'d$8.dll'",
      "'oleaut32.dll'",
      "'ole32.dll'"
   ],
   "Last_Saved":"-",
   "Compilation_Time":"2002-02-05 17:36:26",
   "SHA256":"4013d3c221c6924e8c525aac7ed0402bd5349a28dcbc20bc1ff6bd09079faacf",
   "PDB":[

   ],
   "MD5":"fd7e0ecc41735d3ba0329e1e311689f8",
   "Signatures":[
      {
         "description":"this executable is signed",
         "severity":1
      },
      {
         "description":"one or more potentially interesting buffers were extracted, these generally contain injected code, configuration data, etc.",
         "severity":2
      },
      {
         "description":"allocates read-write-execute memory (usually to unpack itself)",
         "severity":2
      },
      {
         "description":"one or more of the buffers contains an embedded pe file",
         "severity":3
      },
      {
         "description":"executed a process and injected code into it, probably while unpacking",
  }
```

:exclamation:Note that Signatures were made (slightly) based on [Cuckoo Sandbox's Signatures]( https://github.com/cuckoosandbox/community), although it's easy to change that part of the code to fit other signatures :point_up:.


### What's Next
Our future feautures are:
- [ ] Integration with MISP

Probably:
- [ ] Attributes extention

## This tool exists thanks to:

[Neo4J](https://neo4j.com/)

[Docker](https://www.docker.com/)

[Cuckoo Sandbox](https://cuckoosandbox.org)


## Acknowledgments    
Our special thanks to [Nicolas Raus](https://github.com/NicolasRaus) for helping us through the initial stage of this project, and his coding skills that made this possible.

## License
Copyright (c) 2017 Deloitte Argentina

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
