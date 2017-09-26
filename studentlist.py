from string import Template
from os.path import isfile
import xml.etree.ElementTree as et
import codecs

class StudentlistTemplate:
    def __init__(self):
        self.default_templates()

    def default_templates(self):
        self.in_template = {}
        self.in_template['name'] = Template('$COLUMNDATA1 $COLUMNDATA')
        self.in_template['email'] = Template('$COLUMNDATA2')
        self.in_template['phone'] = Template('$COLUMNDATA3')
        self.in_template['parents'] = Template('$COLUMNDATA4')

        self.parent_template = Template('$name,$phone,$email')

        self.out_template = Template('$name,$email,$phone,$parent1\n,,,$parent2\n')

    def birthdaycal(self):
        self.in_template = {}
        self.in_template['name'] = Template('$COLUMNDATA')
        self.in_template['birthday'] = Template('$COLUMNDATA1')

        self.out_template = Template('$name,$birthday;')

class Studentlist:
    def __init__(self):
        self.students = []
        self.error = False
        self.error_msg = ''
        self.templates = StudentlistTemplate()
        

    def load(self, xml = False):
        if xml is False:
            self.error, self.error_msg = True, "no xml supplied"

        try:
            root = et.fromstring(xml)
        except Exception as e:
            self.error, self.error_msg = True, 'load() ' + str(e)
        else:
            for table in root:
                student = {}
                data = {}
                for node in table.iter():
                    data[str(node.tag)] = str(node.text)

                fields = self.templates.in_template.keys()
                for field in fields:
                    student[field] = self.templates.in_template[field].safe_substitute(data)
                
                self.students.append(student)
            if 'parents' in student.keys():
                for s in range(len(self.students)):
                    par = self.students[s]['parents'].split('\n')
                    p_num = 1
                    for p in par:
                        if p != '':
                            parent = {}
                            base = p.split(': ')
                            parent['name'] = base[0]
                            base = base[1].split(', ')
                            parent['phone'] = base[0]
                            parent['email'] = base[1]
                            
                            self.students[s]['parent' + str(p_num)] = self.templates.parent_template.safe_substitute(parent)

                            p_num += 1

                    if 'parent1' not in student.keys():
                        student['parent1'] = ''
                    if 'parent2' not in student.keys():
                        student['parent2'] = ''

            self.error, self.error_msg = False, ''

    def dump(self):
        if not self.error:
            result = ''
            for student in self.students:
                result += self.templates.out_template.safe_substitute(student)

            return result
        return self.error_msg

    def prettyprint(self):
        self.templates.out_template = Template('##########\n[$name]\n@:\t$email\nph:\t$phone\np1:\t$parent1\np2:\t$parent2\n')
        d = self.dump()
        self.templates.default_templates()
        return d
        
    def write(self):
        if not self.error:
            outfilename = self.loadedfile[:self.loadedfile.rfind('.')]
            if outfilename[-1:] in '\/.':
                outfilename += '_ERR'

            i = 0
            collision = True

            while collision:
                ofn = outfilename + str(i) + '.txt'
                if not isfile(ofn):
                    outfilename = ofn
                    collision = False
                i += 1
            
            try:
                with codecs.open(outfilename, 'w', 'mbcs') as outfile:
                    outfile.write(self.dump())
                outfile.close()
            except OSError as e:
                self.error, self.error_msg = True, 'write() ' + str(e)
