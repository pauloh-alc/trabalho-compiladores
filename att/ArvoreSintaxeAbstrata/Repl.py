from Lexer import Lexer
from Parser import Parser
from cmd import Cmd
from Memory import MemoryManager
from SemanticVisitor import Visitor
from CodeGEN import *

class Repl(Cmd):
    prompt = 'UFC> '
    intro = "Bem vindo!\nDigite\n :h para ajuda\n :q para sair e imprimir o assembly\n :s para um exemplo!"

    def do_exit(self, inp):
        return True
    def help_exit(self):
        print('Digite\n :q para sair\n :s para um exemplo!')
        return False
    def emptyline(self): # Disabilita repeticao do ultimo comando
        pass
    def do_s(self):
        print("Samples:")
        print('    1+3*8*(1+2)')
        #print('    let num = 10')
        #print('    num^2')
        #print('    (num+1)*2')
        #print('    let ufc = \"ufc\"')
        #print('    ufc + \"-2024\"')
        return False 
    def default(self, inp):
        if inp == ':q':
            return self.do_exit(inp)
        elif inp == ':h': 
            return self.help_exit()
        elif inp == ':s':
            return self.do_s()            
        self.analisador(inp)
        return False    
    do_EOF = do_exit
    help_EOF = help_exit

    def run(self, linha):
        # Gerar tokens
        lexer = Lexer(linha)
        tokens, error = lexer.makeTokens()
        if error: 
            print(error)
            return None, error
        #print(f'Lexer: {tokens}')

        # Gerar AST
        astInfo = Parser.instance().Parsing(tokens)
        semanticNode, error = astInfo.node, astInfo.error

        if error or not isinstance(semanticNode, Visitor): 
            return None, error
        #print(f'Parser: {semanticNode}')

        # Semantica de tipos para tratar valores na AST (Abstract Syntax Tree), bem como RunTime ou Geracao de Codigo
        generate = CodeGEN()
        managerRT = generate.run(semanticNode) # Aqui chamamos o visit do node da AST, passando o operador de memoria
        return managerRT.value, managerRT.error

    def analisador(self, linha):
        resultado, error = self.run(linha)
        if error: 
            print(f'Log de Erro: {error.printMsg()}')
        else: print(f'{resultado}')
