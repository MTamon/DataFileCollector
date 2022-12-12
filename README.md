# DataFileCollector
To make access to the database easier.

## Usage
The basic usage is as follows.

```python
cond = Condition()
cond.specify_extention(["py"])

collector = Collector(cond, "./")
results = collector.get_path()
results = collector.serialize_path_list(results)

for r in results:
    print(f"collect path: {r}")
```

First, the Condition class is used to condition the file.

In the example above, the function specify_extention() is used to specify that files with ```py``` extension should be extracted.

Next, an instance of the Collector class is created.

The arguments are an instance of the Condition class and the root path of the target database.

The get_path() function returns a list of file paths as list data that preserves the hierarchical structure of the database directory.

If you want to serialize the list, it is recommended to use the serialize_path_list() function.
