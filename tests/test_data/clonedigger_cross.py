#!/usr/bin/python

import xml.sax


def any_of_list_in_string(words, string):
    for word in words:
        if word in string:
            return word
    return None


def print_code(path1, line1, lines):
    with open(path1) as file1:
        for i in range(line1 - 1):
            file1.readline()
        for i in range(lines):
            print file1.readline()[:-1]


class CloneDiggerOutputHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.current_path = None
        self.current_line = "0"
        self.current_loc = 0
        # self.print_code = False
        self.current_tag = ""
        self.words = ["Mutagenesis", "Mutate", "Obb", "Sewer_Diver"]

    def startElement(self, tag, attributes):
        self.current_tag = tag
        if tag == "duplication":
            self.current_loc = int(attributes["lines"])
        elif tag == "file":
            if not self.current_path:
                self.current_path = attributes["path"]
                self.current_line = attributes["line"]
            else:
                word = any_of_list_in_string(self.words, self.current_path)
                if not word in attributes["path"]:
                    print ((("#" * 100) + "\n") * 2)
                    print "Clone size: " + str(self.current_loc)
                    print self.current_path + ": " + self.current_line
                    print "+--------------- Code --------------------+"
                    print_code(self.current_path, int(self.current_line), self.current_loc)
                    print "#"
                    print attributes["path"] + ": " + attributes["line"]
                    print "+--------------- Code --------------------+"
                    print_code(attributes["path"], int(attributes["line"]), self.current_loc)
                    print ""
                    print ((("#" * 100) + "\n") * 2)
                    print "\n"
                    # self.print_code = True
                self.current_path = None
                self.current_line = "0"


                # def characters(self, content):
                # if self.current_tag == "codefragment" and self.print_code:
                # print content
                #         print "\n"
                #         self.print_code = False


def main():
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = CloneDiggerOutputHandler()
    parser.setContentHandler(handler)
    parser.parse("output.xml")


if __name__ == '__main__':
    main()
