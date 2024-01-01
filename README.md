# Geraldine: a static component generator

## About
* Static site generators are kind of heavy weight and specific to creating static sites
* So many things in computer science simply require transforming from one format to another, with some possible tweaks.
* I always loved static site generaters but wanted something a little more flexible, that could just essentially process files how I wanted them to be processed and output a transformed file.
* This is a static component generator. It takes all the things I liked about static site generators like templating, live reload, creating parallel distribution directories, front matter, dev servers, includes, etc. and makes a system that will not only create static sites but also do much more.  
* At a high level it's essentially a file processor.  You put files through one or more processors, i.e. a pipeline, and write the output to disk.
* Use cases:
    * Transpiling to HTML: Convert markdown, jinja, restructured text, TOML, other templating langs -> HTML
    * Transpiling to anything: Converting anything to anything. Just write a plugin!
    * Data population:  Combining JSON plus a template and outputting to a file
        * This also allows one jinja template that can iterate over many elements in json. 
    * Extracting smaller portions of json from large hunks of json.
    * Extracting tags and converting those tags to what they actually represent in the file.
    * Adding cool tweaks to files, like removing any blank lines, indenting entire files 
    * Generating your actual entire website
    * Any which way you want to manhandle a file, you can do it, just write a plugin.

    

## Simple example
* This combines a json template and a jinja template and outputs the result and removes all the blank lines.

* The jinja template file:
```
---
processer: [jinja_parser, remove_blank_lines]
json_path: /somedir/data/myjson.json
---
<div> {{some_variable}}</div>




Foo bar!!!

```
* The data file @ `/somedir.data/myjson.json`:

```
{
    "some_variable":"hello world"
}
```

* run `geri` in the projects root directory and get output:

```
<div>hello world</div>
Foo bar!!
```

* The processor field has two items: jinja_parser, and remove_blank_lines
    * Therefore it process the jinja template, applying the json_path for the data file to apply to the jinja template
    * Then it removed the new lines.
    * The processers operate in order, so it's like a pipeline of one transformation applied, then that data is passed to the next processer.

* Note: this is literally jinja but with front matter and a pipeline to give it more POWAH!


## Directory generation

* Geri has a parent directory with a `geri_src` and a `geri_dest` directory. (names are customizable)

* When `geri` command is run geri iterates through every directory underneath the `geri_src` (or what dirname you specify) in which it was run, processes the and rebuilds the exact directory structure in the sibling `geri_dist` (or what dirname you specify) folder.

* Any files with front matter will be parsed according to the front matter specifications. If no front matter the file will be copied exactly with no processing. 


## More Examples
* see [./geraldine/examples](./geraldine/examples) 

## Install

### Via pypi
* As of this writing, pypi is currently locked to new users due to hackers/spammers lol

### Via wheel (best way)
* You can pip3 install the wheel file from the dist folder and start using `geri` command.
    * `pip3 install geraldine-0.1.0-py3-none-any.whl`

### The long way
1. Clone the repo
2. Install the dependencies in requirements.txt (create a venv if you want)
    * will have to put a bash script in the /bin folder to activate the venv and run the geri command or remember to activate it
3. Add the /bin folder to the path
4. Start using Geraldine with the `geri` command

### Use Poetry
* `poetry install`
* `poetry run python3 cli.py -h`

## CLI
```bash
usage: geri [-h] {info,init,watch,serve} ...

positional arguments:
  {info,init,watch,serve}
                        commands
    info                Show install location
    init                Create source directory for geraldine templates.
    watch               Watch geraldine source folder and rebuild on change.
    serve               Start simple web development server in current directory.

options:
  -h, --help            show this help message and exit


geri info
    Setup info
        install location: /home/nick/.local/lib/python3.10/site-packages/geraldine
        plugin path: /home/nick/.local/lib/python3.10/site-packages/geraldine/plugins
    Available plugins:
        simple_processor.plugin.py
        jinja_parser.plugin.py
        jinja_file_parser.plugin.py
```



## Plugins

* Geri is built with a plugin system, so if you want to create a plugin just drop it into the plugin path with extension: .plugin.py 

* see plugin folder: [./geraldine/plugins](./geraldine/plugins)

* The name of the plugin (without: .plugin.py) will be what you set in the `processer` field in the front matter

* The plugin needs a top level function with the name `geraldine` that gets called by the main system.


* The data passed to geraldine(data) function looks like this:
```
{   
    'destination_path': '/tmp/geri_test/dist/test1/test.jinja.html',
    'frontmatter': {   'extension': 'html',
                       'filename_key': 'class.0.name',
                       'json_path': '/home/nick/bash_shortcuts/in_prog/char_gen/data/json/classes/all_classes.json',
                       'processor': 'jinja_file_parser'},
    'src_path': '/tmp/geri_test/geri_src/test1/test.jinja.html',
    'template_content': '<div>{{class.name}}</div>\n\n',
    'template_filename': 'test.jinja.html'
}

```

* What ever you return from the function will be written to the output file in destination folder
* If you return nothing, no file will be written as it's assumed you're creating the file within the plugin yourself.
* Declare a top level variable to remove an extension from the file name: remove_extensions=['jinja'] 


## Plugins so far
* run `geri info`

## Priority directories
* For things like includes, you can define priority directories.
* This will process everything the same except these directories will be processed first. 
* This allows you to define a jinja template to process and use the include tag with an already built directory: {% include sometemplate.html %} 
* The currently only implemented priority directory so far is geri_src/includes. 
* Going to make this customizable to add any you want when I have the bandwidth


## To Do:
* Stick it up on pypi to make it installable with pip when the hackers/spammers go away
* Make config files
    * a user folder: ~/.geraldine 
    * also project level config files, the code will bubble up looking for the first .geraldine config file match, and use ~/.ger.. as default if none
    * config file for declaring custom things like max-depth, input/output dir, etc.
    * folder for custom plugins
    * priority directories specification
* Add an info variables to the plugin so it outpus info
* the functionality to point the cli at a template with/without front matter and output result to a specified parameter just wtih cli
* Refactor post processing block into its own spot
* Implement yaml and toml processors
* Better docs with examples
* Possibly? move the entire logic to a queue, where a file is processed then put on the queue with metadata, to either be further processed or sent to disk.