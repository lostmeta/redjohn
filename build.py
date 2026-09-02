import os
from string import Template
def build(base_name,template_path,ip,port):
    base_name = os.path.basename(template_path)
    if not os.path.exists(template_path):
        print(f"file {base_name} not found")
    with open(template_path,'r') as f:
            template_content = f.read()
            template = Template(template_content)
            result_code = template.substitute(ip=ip,port=port)
            filename = base_name.replace("template_","gen/")
            with open(f"{filename}","w") as f:
                f.write(result_code)
            print(f"File created in: {filename}")