from Consts import Consts
from SemanticVisitor import *

class Grammar:
    def __init__(self, parser):
        self.parser = parser

    def Rule(self):
        return self.GetParserManager().fail(f"{Error.parserError}: Implementar suas regras de producao (Heranca de Grammar)!")
    
    def CurrentToken(self):
        return self.parser.CurrentTok()
    
    def NextToken(self):
        return self.parser.NextTok()
    
    def GetParserManager(self):
        return self.parser.Manager()

    @staticmethod
    def StartSymbol(parser): # Start Symbol S from Grammar G(V, T, S, P)
        resultado = Exp(parser).Rule()
        if parser.CurrentTok().type != Consts.EOF: return resultado.fail(f"{Error.parserError}: Erro sintatico")
        return resultado
        
class Exp(Grammar): # A variable from Grammar G
    def Rule(self):
        pr = self.GetParserManager()
        if self.CurrentToken().matches(Consts.KEY, Consts.LET):
            self.NextToken()
            if self.CurrentToken().type != Consts.ID:
                return pr.fail(f"{Error.parserError}: Esperado '{Consts.ID}'")
            varName = self.CurrentToken()
            self.NextToken()
            if self.CurrentToken().type != Consts.EQ:
                return pr.fail(f"{Error.parserError}: Esperado '{Consts.EQ}'")
            return self.varAssign(pr, varName)
        
        if (self.CurrentToken().type == Consts.ID):
            if (self.parser.Lookahead(1).type == Consts.EQ):
                varName = self.CurrentToken()
                self.NextToken()
                return self.varAssign(pr, varName)

        if self.CurrentToken().type == Consts.SINGLE_QUOTES:
            if self.parser.Lookahead(2).type == Consts.SINGLE_QUOTES:
                self.NextToken()
                keyName = self.CurrentToken()
                return self.keyAssign(pr, keyName)

        node = pr.registry(NoOpBinaria.Perform(Term(self.parser), (Consts.PLUS, Consts.MINUS)))
        if pr.error:
            return pr.fail(f"{Error.parserError}: Esperado a '{Consts.INT}', '{Consts.FLOAT}', '{Consts.ID}', '{Consts.LET}', '{Consts.PLUS}', '{Consts.MINUS}', '{Consts.LPAR}'")
        return pr.success(node)
    
    def varAssign(self, pr, varName):
        self.NextToken()
        expr = pr.registry(Exp(self.parser).Rule())
        if pr.error: return pr
        return pr.success(NoVarAssign(varName, expr))

    def keyAssign(self, pr, keyName):
        self.NextToken()
        expr = pr.registry(Exp(self.parser).Rule())
        if pr.error: return pr
        return pr.success(NoKeyAssign(keyName, expr))

class Term(Grammar): # A variable from Grammar G
    def Rule(self):
        return NoOpBinaria.Perform(Factor(self.parser), (Consts.MUL, Consts.DIV))

class Factor(Grammar): # A variable from Grammar G
    def Rule(self):
        ast = self.GetParserManager()
        tok = self.CurrentToken()

        if tok.type in (Consts.PLUS, Consts.MINUS):
            self.NextToken()
            factor = ast.registry(Factor(self.parser).Rule())
            if ast.error: return ast
            return ast.success(NoOpUnaria(tok, factor))
        return Pow(self.parser).Rule()

class Pow(Grammar): # A variable from Grammar G
    def Rule(self):
        return NoOpBinaria.Perform(Atom(self.parser), (Consts.POW, ), Factor(self.parser))
    

class ListExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        elementNodes = [] # Checado em Atom: if (self.CurrentToken().type != Consts.LSQUARE): return ast.fail(f"{Error.parserError}: Esperando por '{Consts.LSQUARE}'")        
        self.NextToken()

        if (self.CurrentToken().type == Consts.RSQUARE): # TList vazia
            self.NextToken()
        else:
            elementNodes.append(ast.registry(Exp(self.parser).Rule()))
            if (ast.error!=None):
                return ast.fail(f"{Error.parserError}: Esperando por '{Consts.RSQUARE}', '{Consts.KEYS[Consts.LET]}', '{Consts.INT}', '{Consts.FLOAT}', '{Consts.ID}', '{Consts.PLUS}', '{Consts.MINUS}', '{Consts.LPAR}', '{Consts.LSQUARE}'")
            
            while (self.CurrentToken().type == Consts.COMMA):
                self.NextToken()

                elementNodes.append(ast.registry(Exp(self.parser).Rule()))
                if (ast.error!=None): return ast

            if (self.CurrentToken().type != Consts.RSQUARE):
                return ast.fail(f"{Error.parserError}: Esperando por '{Consts.COMMA}' ou '{Consts.RSQUARE}'")
            self.NextToken()
        
        return ast.success(NoList(elementNodes))


class TuplaExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        elementNodes = []
        self.NextToken()

        if (self.CurrentToken().type == Consts.RPAR):  # TTuple vazia
            self.NextToken()
        else:
            elementNodes.append(ast.registry(Exp(self.parser).Rule()))
            if (ast.error != None):
                return ast.fail(
                    f"{Error.parserError}: Esperando por '{Consts.RPAR}', '{Consts.KEYS[Consts.LET]}', '{Consts.INT}', '{Consts.FLOAT}', '{Consts.ID}', '{Consts.PLUS}', '{Consts.MINUS}', '{Consts.LPAR}', '{Consts.LSQUARE}'")

            while (self.CurrentToken().type == Consts.COMMA):
                self.NextToken()

                elementNodes.append(ast.registry(Exp(self.parser).Rule()))
                if (ast.error != None): return ast

            if (self.CurrentToken().type != Consts.RPAR):
                return ast.fail(f"{Error.parserError}: Esperando por '{Consts.COMMA}' ou '{Consts.RPAR}'")
            self.NextToken()

        return ast.success(NoTuple(elementNodes))


class DictExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        elementNodes = []
        self.NextToken()

        if (self.CurrentToken().type == Consts.RCURLY_BRACE):  # TTuple vazia
            self.NextToken()
        else:
            elementNodes.append(ast.registry(Exp(self.parser).Rule()))
            if (ast.error != None):
                return ast.fail(
                    f"{Error.parserError}: Esperando por '{Consts.RCURLY_BRACE}', '{Consts.KEYS[Consts.LET]}', '{Consts.INT}', '{Consts.FLOAT}', '{Consts.ID}', '{Consts.PLUS}', '{Consts.MINUS}', '{Consts.LPAR}', '{Consts.LSQUARE}'")

            while (self.CurrentToken().type == Consts.COMMA):
                self.NextToken()

                elementNodes.append(ast.registry(Exp(self.parser).Rule()))
                if (ast.error != None): return ast

            if (self.CurrentToken().type != Consts.RCURLY_BRACE):
                return ast.fail(f"{Error.parserError}: Esperando por '{Consts.COMMA}' ou '{Consts.RCURLY_BRACE}'")
            self.NextToken()

        return ast.success(NoDict(elementNodes))

class Atom(Grammar): # A variable from Grammar G
    def Rule(self):
        ast = self.GetParserManager()
        tok = self.CurrentToken()
        if tok.type in (Consts.INT, Consts.FLOAT):
            self.NextToken()
            return ast.success(NoNumber(tok))        
        elif(tok.type == Consts.STRING):
            self.NextToken()
            return ast.success(NoString(tok))
        elif tok.type == Consts.ID:
            self.NextToken()
            return ast.success(NoVarAccess(tok))
        elif tok.type == Consts.LPAR:
            tuple_exp = ast.registry(TuplaExp(self.parser).Rule())
            if ast.error: return ast
            return ast.success(tuple_exp)
        elif tok.type == Consts.LSQUARE:
            listExp = ast.registry(ListExp(self.parser).Rule())
            if (ast.error != None): return ast
            return ast.success(listExp)
        elif tok.type == Consts.LCURLY_BRACE:
            dictExp = ast.registry(DictExp(self.parser).Rule())
            if (ast.error != None): return ast
            return ast.success(dictExp)
            
        return ast.fail(f"{Error.parserError}: Esperado por '{Consts.INT}', '{Consts.FLOAT}', '{Consts.ID}', '{Consts.LET}', '{Consts.PLUS}', '{Consts.MINUS}', '{Consts.LPAR}', '{Consts.GRAPH}'")

