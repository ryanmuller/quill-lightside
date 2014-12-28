# Quill Lightside

Access to the LightSide API and a minimal web application demonstrating its use.

## Usage

The syntax is inspired by Rails ActiveRecord: resources have `find` taking an id (int or string) and `create` taking attributes as parameters. Associations can be fetched with a method named as the resource. 

This example finds a Lightbox by id and returns its name and Prompt text (through the Grader).

```python
lightbox = Lightbox.find(lightbox_id)
grader = lightbox.grader()
prompt = grader.prompt()
return { 'name': lightbox.name(),
         'prompt': prompt.text() }
```
