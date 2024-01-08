# Geraldine: a static component generator

## About
* This is a static component generator. It takes data and templates with front matter and outputs a processed file.  
* At a high level it's essentially a file processor with bells and whistles.  You put files through one or more processors, i.e. a pipeline, and write the output to disk.
* Use cases:
    * Transpiling to HTML: Convert markdown, jinja, restructured text, TOML, other templating langs -> HTML
    * Transpiling to anything: Converting anything to anything. Just write a plugin!
    * Data population:  Combining JSON plus a template and outputting to a file
        * This also allows one jinja template that can iterate over many elements in json. 
    * Extracting smaller portions of json from large hunks of json.
    * Extracting tags and converting those tags to what they actually represent in the file.
    * Adding cool tweaks to files, like removing any blank lines, indenting entire files, prettifying code
    * Minimizing, obfuscating
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

* Note: this is literally jinja but with front matter and a pipeline to give it more power!


## Directory generation
* Geri has a parent directory with a `geri_src` and a `geri_dest` directory. (names are customizable)

* When `geri` command is run geri iterates through every directory underneath the `geri_src` (or what dirname you specify) in which it was run, processes the and rebuilds the exact directory structure in the sibling `geri_dist` (or what dirname you specify) folder.

* Any files with front matter will be parsed according to the front matter specifications. If no front matter the file will be copied exactly with no processing. 

* Important: `geri_dest` (or whatever your custom destination directory) is continually completely wiped. 
    * Nothing in here is supposed to modified except via `geri_src`.  
    * `geri_dest` is supposed to be an ephemeral mirror of `geri_src`
    * Also, Please do not customize the destination folder to a folder with important data in it, as it will be wiped!!!

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
* geri has a cli.  `geri --help`


## Plugins
* In geraldine: processor == module == plugin
    * plugin is what the files are called
    * module is whats called in the code of the system
    * processor is what it's called in the front matter of template files
    * they all refer to the same thing though.

* Geri is built with a plugin system, so if you want to create a plugin just drop it into the plugin path with extension: .plugin.py 

* see plugin folder for examples: [./geraldine/plugins](./geraldine/plugins)

* The name of the plugin (without: .plugin.py) will be what you set in the `processer` field in the front matter

* The plugin needs a top level function with the name `geraldine` that gets called by the main system.

* There is a lot of data passed to the plugins geraldine function. You can run a print statement or json.dumps in a custom plugin on it to see what all is being passed.
    * Going to add more documentation on this at some point

* What ever you return from the function will go through the other processors you've specified and then be written to the output file in destination folder
* If you return nothing, no file will be written as it's assumed you're creating the file within the plugin yourself, and geri will move on to the next file in the source directory.

* Declare a top level variable to remove an extension from the file name: remove_extensions=['jinja'] 

* If you run `geri init` in your project folder it will create a .geraldine folder with a config file and a custom plugins directory.

## Built in plugins so far
* run `geri info`

## Priority directories
* For things like includes, you can define priority directories.
* This will process everything the same except these directories will be processed first. 
* This allows you to define a jinja template to process and use the include tag with an already built directory: {% include sometemplate.html %} 
* The currently builtin priority directory geri_src/includes, but you can specify with the config file built with `geri init`. 

## Caveats
* This is just a single thread working on a single file at a time that is loaded into memory. 
    * Have not tested extreme use cases like massive numbers of files or gigantic files.
    * I'm working with over a thousand files in one project and having no issues.  
    * I don't see why giant files should be much of an issue as long as they're under your allowed process memory size 
    * There's ways I've thought of to optimize this like having a queue and workers and tags for large files to trigger line by line processing, but don't have the time presently.
* I have not tested this on any OS but Ubuntu 22, although tried to code it to be OS agnostic


## To Do:
* Stick it up on pypi to make it installable with pip when the hackers/spammers go away
* The functionality to point the cli at a template with/without front matter and output result to a specified parameter just wtih cli
* Refactor post processing block into its own spot
* Implement yaml and toml processors, html/json/etc. prettifiers
* Expanded docs with more examples
* Add documentation functionality to processor/module/plugins 