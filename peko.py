from arrow_error import *


################################################
### CONTANS 
################################################
NUM = '0123456789'

################################################
### ERROR 
################################################

class Error:
  def __init__(self, post_start, post_end, error_name, details):
    self.post_start = post_start
    self.post_end = post_end
    self.error = error_name
    self.detail = details
  
  def as_string(self):
    results = f'Yabai peko.. {self.error}: {self.detail}\nFile {self.post_start.fn}, Line {self.post_end.ln + 1}\n\n{string_with_arrows(self.post_start.ftxt, self.post_start, self.post_end)}'
    return results
    
class IlegalCharError(Error):
  def __init__(self, post_start, post_end, details):
    super().__init__(post_start, post_end, 'found illegal character', details)

class InvalidSyntaxError(Error):
  def __init__(self, post_start, post_end, details):
    super().__init__(post_start, post_end, 'invalid syntax', details)

################################################
### POSITIONS 
################################################
class Postition:
  def __init__(self, idx, ln, col, fn, ftxt):
    self.idx = idx
    self.ln = ln
    self.col = col
    self.fn = fn
    self.ftxt = ftxt
  def advance(self, current_char=None):
    self.idx +=1
    self.col +=1
    
    if current_char == "\n":
      self.ln += 1
      self.col = 0
    return self
  
  def copy(self):
    return Postition(self.idx, self.ln, self.col, self.fn, self.ftxt)
  
################################################
### TOKENS 
################################################
INT = "INT"
FLOAT = "FLOAT"
PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
DIV = "DIV"
LPARENT = "LPARENT"
RPARENT = "RPARENT"
EOF = "EOF"


class Token:
  def __init__(self, type_, value=None, post_start=None, post_end=None):
    if post_start:
      self.post_start = post_start.copy()
      self.post_end = post_start.copy()
      self.post_end.advance()
    if post_end:
      self.post_end = post_end
    self.type = type_
    self.value = value
  def __repr__(self):
    if self.value: return f"{self.type}:{self.value}"
    return f"{self.type}"
    
################################################
### LEXER 
################################################

class Lexer:
  def __init__(self, fn, text):
    self.text = text
    self.fn = fn
    self.post = Postition(-1, 0, -1, fn, text)
    self.current_char = None
    self.advance()
    
  def advance(self):
    self.post.advance(self.current_char)
    self.current_char = self.text[self.post.idx] if self.post.idx < len(self.text) else None
    
  def make_tokens(self):
    TOKENS = []
    while self.current_char != None:
      if self.current_char in ' \t':
        self.advance()
      elif self.current_char in NUM:
        TOKENS.append(self.make_number())
        self.advance()
      elif self.current_char == '+':
        TOKENS.append(Token(PLUS, post_start=self.post))
        self.advance()
      elif self.current_char == '-':
        TOKENS.append(Token(MINUS, post_start=self.post))
        self.advance()
      elif self.current_char == '*':
        TOKENS.append(Token(MUL, post_start=self.post))
        self.advance()
      elif self.current_char == '/':
        TOKENS.append(Token(DIV, post_start=self.post))
        self.advance()
      elif self.current_char == '(':
        TOKENS.append(Token(LPARENT, post_start=self.post))
        self.advance()
      elif self.current_char == ')':
        TOKENS.append(Token(RPARENT, post_start=self.post))
        self.advance()
      else:
        # RETURN ERROR
        pos_start = self.post.copy()
        char = self.current_char
        self.advance()
        return [], IlegalCharError(pos_start, self.post, f"'{char}'")
    
    TOKENS.append(Token(EOF, post_start=self.post))
    return TOKENS, None
  
  def make_number(self):
    num_str = ''
    dot_count = 0
    post_start = self.post.copy()
    
    while self.current_char != None and self.current_char in NUM + ".":
      if self.current_char == ".":
        if dot_count == 1: break
        dot_count +=1
        num_str += "."
      else:
        num_str += self.current_char
      self.advance()
      
    if dot_count == 0:
      return Token(INT, int(num_str), post_start, self.post)
    else:
      return Token(FLOAT, float(num_str), post_start, self.post)
      
################################################
### NODES 
################################################
class NumberNode:
  def __init__(self, tok):
    self.tok = tok
    
    self.post_start = self.tok.post_start
    self.post_end = self.tok.post_end
  
  def __repr__(self):
    return f'{self.tok}'
    
class BinOpNode:
  def __init__(self, left_node, op_token, right_node):
    self.left_node = left_node
    self.op_token = op_token
    self.right_node = right_node
    
    self.post_start = self.left_node.post_start
    self.post_end = self.right_node.post_end
  
  def __repr__(self):
    return f'({self.left_node}, {self.op_token}, {self.right_node})'

class UnaryOpNode:
  def __init__(self, op_tok, node):
    self.op_tok = op_tok
    self.node = node
    
    self.post_start = self.op_tok.post_start
    self.post_end = node.post_end
    
  def __repr__(self):
    return f'({self.op_tok} {self.node})'
  
################################################
### PARSER RESULTS
################################################
class ParseResult:
  def __init__(self):
    self.error = None
    self.node = None
    
  def register(self, res):
    if isinstance(res, ParseResult):
      if res.error: self.error = res.error
      return res.node
    return res
  
  def success(self, node):
    self.node = node
    return self
  def failure(self, error):
    self.error = error
    return self

################################################
### PARSER
################################################
class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.tok_idx = -1
    self.advance()
    
  def advance(self):
    self.tok_idx += 1
    if self.tok_idx < len(self.tokens):
      self.current_tok = self.tokens[self.tok_idx]
    return self.current_tok
    
  def parse(self):
    res = self.expr()
    if not res.error and self.current_tok.type != EOF:
      return res.failure(InvalidSyntaxError(
        self.current_tok.post_start, self.current_tok.post_end,
        "Unexpected +, -, or /"
      ))
    return res
  
  def factor(self):
    res = ParseResult()
    tok = self.current_tok
    
    if tok.type in (PLUS, MINUS):
      res.register(self.advance())
      factor = res.register(self.factor())
      if res.error: return res
      return res.success(UnaryOpNode(tok, factor))
    
    elif tok.type in (INT, FLOAT):
      res.register(self.advance())
      return res.success(NumberNode(tok))
    
    elif tok.type == LPARENT:
      res.register(self.advance())
      expr =  res.register(self.expr())
      if res.error: return res
      if self.current_tok.type == RPARENT:
        res.register(self.advance())
        return res.success(expr)
      else:
        return res.failure(InvalidSyntaxError(
          tok.post_start, tok.post_end,
          "Unexpected ')'"
        ))
      
    return res.failure(InvalidSyntaxError(
      tok.post_start, tok.post_end,
      'Unexpected int or float'
    ))
  
  def term(self):
    return self.bin_op(self.factor, (MUL, DIV))
 
  def expr(self):
    return self.bin_op(self.term, (PLUS, MINUS))
  
  def bin_op(self, func, ops):
    res = ParseResult()
    left = res.register(func())
    if res.error: return res
    
    while self.current_tok.type in ops:
      op_tok = self.current_tok
      res.register(self.advance())
      right = res.register(func())
      if res.error: return res
      left = BinOpNode(left, op_tok, right)
    
    return res.success(left)
    
################################################
### VALUES 
################################################
class Number:
  def __init__(self, value):
    self.value = value
    self.set_post()
    
  def set_post(self, post_start=None, post_end=None):
    self.post_start = post_start
    self.post_end = post_end
    return self
    
  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value)
      
  def sum_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value)
  
  def mul_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value)
      
  def div_by(self, other):
    if isinstance(other, Number):
      return Number(self.value / other.value)
      
  def __repr__(self):
    return str(self.value)
  
################################################
### INTERPRETER 
################################################
class Interpreter:
  def visit(self, node):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node)
  
  def no_visit_method(self, node):
    raise Exception(f'No visit_{type(node).__name__} method defined')
  
  def visit_NumberNode(self, node):
    return Number(node.tok.value).set_post(node.post_start, node.post_end)
    
  def visit_BinOpNode(self, node):
    left = self.visit(node.left_node)
    right = self.visit(node.right_node)
    
    if node.op_token.type == PLUS:
      results = left.added_to(right)
    
    elif node.op_token.type == MINUS:
      results = left.sum_by(right)
    
    elif node.op_token.type == MUL:
      results = left.added_to(right)
    
    return results.set_post(node.post_start, node.post_end)
  
  def visit_UnaryOpNode(self, node):
    number = self.visit(node.node)
    
    if node.op_tok.type == MINUS:
      number = number.mul_by(Number(-1))
    
    return number.set_post(node.post_start, node.post_end)
  
################################################
### RUN 
################################################

def run(fn, text):
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error
  
  # Generate AST
  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error
  
  # Run Program
  interpreter = Interpreter()
  results = interpreter.visit(ast.node)
  
  return  results, None