# UML 4 Markdown

This tools will modify the provided md file.
It well search for blocks wraped in three quotes and labels `uml`
A hash of the contence of the block will be created and used to see if there has been any modification.
The uml code block will be wrapped in a details block and prior to the section block, an markdoen image will exist pointint to a .img/<hash>.png file.
If the has fails to match, the old image shoudl be deleted and a new image created in the .img folder/

The new image will be created using plantuml.   the content of the code block should be samed to the /tmp folder as <hash>.  The saved data should be wraped with `@startuml` and `@enduml`.   A uml threme file may also be applied.


before:
```

    ```uml
        Alice -> Bob : hello
    ```

```

After:

```
   ![](.img/xxxxxxxxxxxx.png) 
    <details>
    <summary>View UML</summary>
    ```uml
        Alice -> Bob : hello
    ```
    <details>

```
where xxxxxxxxxxxx is the md5 




Example command line:
```bash
updatemd.py README.py

```





## example

```uml

Alice -> Bob : hello

```


## Example .umltheme file

If the following .umltheame file may exist in the same folder as the md file or in teh repo root.
This file will be added to the `@startuml` in teh created uml files

```
!theme toy
skinparam handwritten true
skinparam DefaultFontName "Comic Sans MS"
skinparam defaultTextAlignment center
```




