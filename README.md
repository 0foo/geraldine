# Geraldine: a static component generator

* Do you have a bunch of JSON or YAML or TOML you want to convert to html components to keep your browser code clean?

* Geraldine converts string templates with front matter into html:



```
(/somedir/components/geri_src/helloworld/mytemplate.jinja.html)
---
processer: jinja_parser 
json_path: /somedir/data/myjson.json
---
<div> {{some_variable}}</div>

```

```
(/somedir/data/myjson.json)
{
    "some_variable":"hello world"
}
```

* run `geri` in `/somedir/components` and get output:

```
(/somedir/components/dist/helloworld/mytemplate.html)
<div>hello world</div>
```

* Geri iterates through every directory underneath the `geri_src` in which it was run and rebuilds the directory structure in the sibling `dist` folder.
    * (has a max depth of 10, but can be changed if needed in the source code)
* If it encounters a file with front matter geri will parse the front matter with the json specified in the example. If no front matter the file will be copied exactly. 


## Examples
* see [./geraldine/examples](./geraldine/examples) 

## Install

### Via pypi
* As of this writing, pypi is currently locked to new users due to some suspicious stuff going on.

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

* The name of the plugin will be set in the `processer` field in the front matter

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
* jinja_parser
    * Simply point the front matter at a json with the the  json_path attribute. 
    * If the json is complex can use a start_key element which populates the template with the value at that key instead of starting at the root of the json.
        * the semantics for this are standard jq or jinja json traversal
```
processor: jinja_parser
json_path: ../../../all_classes.json
start_key: 0.class.0
---
<div>{{name}}</div>

```


* jinja_file_parser
    * Creates a file from every element in the json key using this template
    * i.e. if the json key points to an array of json, will create a new file for each json element in the array.

```
---
processor: jinja_file_parser
json_path: ../../../all_classes.json
filename_key: class.0.name
extension: html
---

<div>{{class.0.name}}</div>
```

## Priority directories
* For things like includes, you can define priority directories.
* This will process everything the same except these directories will be processed first. 
* This allows you to define a jinja template to process and use the include tag: {% include sometemplate.html %} 
* The currently only implemented priority directory is geri_src/includes.

## To Do:
* Stick it up on pypi to make it installable with pip
* Make config files
    * a user folder: ~/.geraldine 
    * also project level config files, the code will bubble up looking for the first .geraldine config file match, and use ~/.ger.. as default if none
    * config file for declaring custom things like max-depth, input/output dir, etc.
    * folder for custom plugins
    * priority directories
* the functionality to point the cli at a template with/without front matter and output result to a specified parameter just wtih cli
* Refactor post processing block into its own spot
* Implement yaml and toml processors
* Better docs with examples
* Move the entire logic to a queue, where a file is processed then put on the queue with metadata, to either be further processed or sent to disk.
* Tests