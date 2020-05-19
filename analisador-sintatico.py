import re
import traceback

######################################
########### Code Analyzer ############
######################################

def lines(index, error_list, after_or_but_received, last_token, error_type):
	lines = code.split('\n')
	line = 0
	size = 0
	for line in range(len(lines)):
		size += len(lines[line]) + 1
		# print(lines[line], len(lines[line]), size, index)
		
		line += 1
		if(index < size):
			line -= 1
			size = size - len(lines[line]) - 1
			
			break

	spaces = ""
	for i in range(size, index - 1):
		if(code[i] == "\t"):
			spaces += "\t"
		else:
			spaces += " "

	expected = "'" + error_list[0][0] + "'"
	for i in range(1, len(error_list)):
		expected += " or '" + error_list[i][0]+"'"

	if(error_type == 'Lexical error'):
		last_token = error_list[-1][3] 

	print("{}: line {}\n\n{}\n{}^\nExpected {} {} '{}'.".format(error_type, line + 1, lines[line], spaces, expected, after_or_but_received, last_token))

	print()

def filterErrorList(token, index, error_list):
	new_error_list = []
	for error in error_list:
		if(error[4] == index and error[2] == token):
			new_error_list.append(error)

	return new_error_list


def replaceToken(new_token, old_token, index):
	if(new_token == 'numero_int'):
		new_token = '1'
	elif(new_token == 'numero_real'):
		new_token = '1.0'

	size = len(old_token)
	index = index - size
	substring = code[index:]
	substring = substring.replace(old_token, " " + new_token + " ", 1)
	return code[:index] + substring

def putBeforeToken(new_token, old_token, index):
	if(new_token == 'numero_int'):
		new_token = '1'
	elif(new_token == 'numero_real'):
		new_token = '1.0'

	size = len(old_token)
	index = index - size
	substring = code[index:]
	return code[:index] + " " + new_token + " " + substring




######################################
######### Lexical Analyzer ###########
######################################

def removeComments():
	return re.sub("{[\n]*.*x*}|{[\n]*.*x*", ' ', code)

def isNumber(char):
    return (ord(char) > 47 and ord(char) < 58)

def isChar(char):
	return (ord(char) > 64 and ord(char) < 91) or (ord(char) > 96 and ord(char) < 123)

def getColumnNumberOfInputChar(char):
	if(char == '\n' or char == ' ' or char == '\t'):
		return 0
	elif(isNumber(char)):
		return 1
	elif(isChar(char)):
		return 2
	else:
		entry_symbols  = ['.', ';', ':', ',', '(', ')', '=', '<', '>', '+', '-', '*', '/']
		if char in entry_symbols:
			return entry_symbols.index(char) + 3
		else:
			return 16

def replaceIdentIfReservedWord(token):
	if(token[0] == alias[1]):
		reserved_words = ["program", "begin", "end", "var", "procedure","else", "read", "write", "while", "do", "if", "then", "real", "integer"]
		
		if(token[2] in reserved_words):
			token[0] = reserved_words[reserved_words.index(token[2])]


def getNextToken(starting_index):
	index = starting_index
	current_state = 0
	sequence = ''

	# while index didnt reach the end of the code
	while(index < len(code)):

		entry_sequence = code[index]					
		entry_number = getColumnNumberOfInputChar(entry_sequence)
		next_state = states[current_state][entry_number]

		if(entry_sequence == "{"):

			if(len(sequence) > 0):
				break

			index += 1
			while(code[index] != "}"):
				index += 1
				if (index == len(code)):
					break
			

			index += 1	
			if (index == len(code)):
				break

			entry_sequence = code[index]					
			entry_number = getColumnNumberOfInputChar(entry_sequence)
			next_state = states[current_state][entry_number]


		# if \n \t or \space
		if(current_state == 0 and entry_number == 0):
			# do nothing
			sequence = sequence

		else:	

			# if whole sequence possible was found
			if(next_state == 0):

				# then return token
				token = [alias[current_state], index, sequence]
				replaceIdentIfReservedWord(token)
				return token
			
			current_state = next_state
			sequence += code[index]

		index += 1

	# if index reached end, then return token
	token = [alias[current_state], index, sequence]
	replaceIdentIfReservedWord(token)
	return token


############################
######### Parser ###########
############################

def parser():

	log_list = []

	grammar_id_stack = []
	grammar_stack = []
	state_stack = []
	entry_index_stack = []
	came_from_empty_state = []

	using_sequence_stack = []
	using_token_stack = []
	using_token_index_stack = []
	
	grammar_id = 0

	not_using_sequence_stack = []
	not_using_token_stack = []
	not_using_token_index_stack = []

	current_grammar_name = grammars[0]
	current_state = 0
	current_entry_index = 0


	index = 0
	token = getNextToken(index)
	current_token = token[0]
	index = token[1]
	current_sequence = token[2]

	current_grammar_data = []
	current_grammar = []
	possible_tokens = []
	possible_grammars = []

	error_list = []

	success = False

	try:
		while True:

			success = False
			current_grammar_data = grammarDecoder(current_grammar_name)
			current_grammar = current_grammar_data[0]
			current_possible_tokens = current_grammar_data[1]
			current_possible_grammars = current_grammar_data[2]

			# print(current_token, current_grammar_name, current_state, current_entry_index)


			empty_index = len(current_possible_tokens) + len(current_possible_grammars)
			not_successful = False
			if(current_entry_index < empty_index):
				while(current_grammar[current_state][current_entry_index] == "error"):
					current_entry_index += 1
					if(current_entry_index == empty_index):
						not_successful = True
						break

			else:
				not_successful = True
				
			# print(current_token, current_grammar_name, current_state, current_entry_index)

			# print(current_token, current_grammar_name, current_state, current_entry_index)

			if(not not_successful):
				
				# print(current_token, current_grammar_name, current_state, current_entry_index)

				if(current_entry_index < len(current_possible_tokens)):
					if(current_token == current_possible_tokens[current_entry_index]):

						result = current_grammar[current_state][current_entry_index]

						if(type(result) == int):
							# print(current_token, current_grammar_name, current_state, current_entry_index)
							# print('salvei')
							grammar_stack.append(current_grammar_name)
							state_stack.append(current_state)
							entry_index_stack.append(current_entry_index)
							grammar_id_stack.append(grammar_id)
							came_from_empty_state.append(False)
							log_list.append([current_token, current_grammar_name, current_state, current_entry_index , 'success'])
							using_token_stack.append(current_token)
							using_sequence_stack.append(current_sequence)
							using_token_index_stack.append(index)
							current_state = result

							if(hasNextToken(not_using_token_stack)):
								current_token = not_using_token_stack.pop()
								index = not_using_token_index_stack.pop() ######################
								current_sequence = not_using_sequence_stack.pop()

							else:
								token = getNextToken(index)
								current_token = token[0]
								index = token[1]
								current_sequence = token[2]

						else:

							# print('SUCCESSO TOKEN')

							# print(current_token, current_grammar_name, current_state, current_entry_index)
							# print('salvei')

							success = True
							log_list.append([current_token, current_grammar_name, current_state, current_entry_index , 'success'])

							grammar_stack.append(current_grammar_name)
							state_stack.append(current_state)
							entry_index_stack.append(current_entry_index)
							grammar_id_stack.append(grammar_id)
							came_from_empty_state.append(False)

							k = 1
							while True:

								

								# k = 0
								initial_k = k

								while (grammar_id != grammar_id_stack[-initial_k] - 1):
									k += 1
									current_grammar_name = grammar_stack[-k]
									current_state = state_stack[-k]
									current_entry_index = entry_index_stack[-k]
									grammar_id = grammar_id_stack[-k]

								current_grammar_data = grammarDecoder(current_grammar_name)
								current_grammar = current_grammar_data[0]

								result = current_grammar[current_state][current_entry_index]
								if(type(result) == int):
									# print('agora eu saio do loop', current_grammar_name, grammar_stack, current_entry_index)
									
									
									using_token_stack.append(current_token)
									using_token_index_stack.append(index)
									using_sequence_stack.append(current_sequence)

									current_state = result
									current_entry_index = 0

									break

							if(hasNextToken(not_using_token_stack)):
								current_token = not_using_token_stack.pop()
								index = not_using_token_index_stack.pop() ##############################
								current_sequence = not_using_sequence_stack.pop()

							else:
								token = getNextToken(index)
								current_token = token[0]
								index = token[1]
								current_sequence = token[2]

						current_entry_index = 0

					else:

						current_entry_index += 1

				else:
					# print('SUCCESSO GRAMMAR')
					grammar_stack.append(current_grammar_name)
					state_stack.append(current_state)
					entry_index_stack.append(current_entry_index)
					grammar_id_stack.append(grammar_id)
					came_from_empty_state.append(False)
					possible_tokens_length = len(current_possible_tokens)
					current_grammar_name = current_possible_grammars[current_entry_index - possible_tokens_length]
					current_state = 0
					current_entry_index = 0
					grammar_id += 1



			else:

				empty_result = current_grammar[current_state][-1]
				
				if(current_entry_index > empty_index):

					empty_result = "error"

				if(empty_result == "error"):
					
					# print('ERRO VAZIO')

					for token_index in range(len(current_possible_tokens)):
						if(current_grammar[current_state][token_index] != 'error'):
							error_list.append([current_possible_tokens[token_index], current_state, current_token, current_sequence, index, current_grammar_name, current_grammar[current_state][token_index]])

					# print("OLHA AQUI")
					# print(using_token_stack)
					# print(grammar_stack)
					# print(came_from_empty_state)
					# print(state_stack)
					empty_state = came_from_empty_state.pop()
					if(current_state != 0 and not empty_state):
						not_using_token_stack.append(current_token)
						not_using_token_index_stack.append(index)
						not_using_sequence_stack.append(current_sequence)

						current_token = using_token_stack.pop()
						index = using_token_index_stack.pop()
						current_sequence = using_sequence_stack.pop()


					# print('deu ruim', current_token, grammar_stack)
					# print(current_state, current_grammar_name)
					current_grammar_name = grammar_stack.pop()
					current_state = state_stack.pop()
					grammar_id = grammar_id_stack.pop()

					# print('new_token', current_token)
					# print(using_token_stack)
					current_entry_index = entry_index_stack.pop()

					current_entry_index += 1


				else:

					# input()
					success = True
					grammar_stack.append(current_grammar_name)
					state_stack.append(current_state)
					entry_index_stack.append(current_entry_index)
					grammar_id_stack.append(grammar_id)
					came_from_empty_state.append(True)
					k = 1
					while True:

						
						
						
						# k = 0
						initial_k = k
						# print('a')
						# print(grammar_id_stack[-initial_k])
						# print(grammar_id_stack)
						# print(current_state, current_grammar_name, grammar_stack, grammar_id_stack)
						while (grammar_id != grammar_id_stack[-initial_k] - 1):
							# print(current_state, grammar_id)
							k += 1
							current_grammar_name = grammar_stack[-k]
							current_state = state_stack[-k]
							current_entry_index = entry_index_stack[-k]
							grammar_id = grammar_id_stack[-k]
							# print(k)

							

						# print('SUCCESSO VAZIO')
						# print(current_token, index, current_grammar_name, current_state, current_entry_index)
						# print('vish')
						current_grammar_data = grammarDecoder(current_grammar_name)
						current_grammar = current_grammar_data[0]

						result = current_grammar[current_state][current_entry_index]
						
						# print(result)
						if(type(result) == int):

							current_state = result
							current_entry_index = 0

							break


	except:


		# traceback.print_exc()
		print()

	

	# for item in log_list:
	# 		print(item)

	if(success):
		token = getNextToken(index)
		if(token[0] == 'inicial'):
			print('No error, compiled with success.')
			return None
		else:
			lines(token[1], [['EOF']], 'after', '.', 'Syntax error')
			return []

	else:

		if(len(not_using_token_stack) > 0):
			log_list.append([not_using_token_stack[0],  not_using_token_index_stack[0], 'error'])
		else:
			log_list.append([current_token,  index, 'error'])
		

		# for item in log_list:
		# 	print(item)

		# print()
		# for item in error_list:
		# 	print(item)

		# print()
		if(len(not_using_token_stack) > 0):
			error_list = filterErrorList(not_using_token_stack[0], not_using_token_index_stack[0] ,error_list)
		else:
			error_list = filterErrorList(log_list[-1][0], index, error_list)

		# for item in error_list:
		# 	print(item)

		after_or_but_received = "but received"
		last_token = log_list[-1][0]

		if(log_list[-1][0] == "inicial"):
			after_or_but_received = "after"
			last_token = log_list[-2][0]
		
		if(log_list[-1][0] == "erro_lexico"):
			lines(log_list[-1][1], error_list, after_or_but_received, last_token, 'Lexical error')
		else:
			lines(log_list[-1][1], error_list, after_or_but_received, last_token, 'Syntax error')
		
		if(after_or_but_received != "after"):			
			return error_list
		else:
			return None

	



def hasNextToken(stack):
	return len(stack) > 0

def findTerminalSymbol(current_token, possible_tokens):
	if current_token in possible_tokens:
		return possible_tokens.index(current_token)

	return -1




def grammarDecoder(grammar_name):
	if(grammar_name == "PROGRAMA"):
		return [PROGRAMA_grammar, PROGRAMA_possible_tokens, PROGRAMA_possible_grammars]
	elif(grammar_name == "CORPO"):
		return [CORPO_grammar, CORPO_possible_tokens, CORPO_possible_grammars]
	elif(grammar_name == "DC"):
		return [DC_grammar, DC_possible_tokens, DC_possible_grammars]
	elif(grammar_name == "DC_V"):
		return [DC_V_grammar, DC_V_possible_tokens, DC_V_possible_grammars]
	elif(grammar_name == "TIPO_VAR"):
		return [TIPO_VAR_grammar, TIPO_VAR_possible_tokens, TIPO_VAR_possible_grammars]
	elif(grammar_name == "VARIAVEIS"):
		return [VARIAVEIS_grammar, VARIAVEIS_possible_tokens, VARIAVEIS_possible_grammars]
	elif(grammar_name == "MAIS_VAR"):
		return [MAIS_VAR_grammar, MAIS_VAR_possible_tokens, MAIS_VAR_possible_grammars]
	elif(grammar_name == "DC_P"):
		return [DC_P_grammar, DC_P_possible_tokens, DC_P_possible_grammars]
	elif(grammar_name == "PARAMETROS"):
		return [PARAMETROS_grammar, PARAMETROS_possible_tokens, PARAMETROS_possible_grammars]
	elif(grammar_name == "LISTA_PAR"):
		return [LISTA_PAR_grammar, LISTA_PAR_possible_tokens, LISTA_PAR_possible_grammars]
	elif(grammar_name == "MAIS_PAR"):
		return [MAIS_PAR_grammar, MAIS_PAR_possible_tokens, MAIS_PAR_possible_grammars]
	elif(grammar_name == "CORPO_P"):
		return [CORPO_P_grammar, CORPO_P_possible_tokens, CORPO_P_possible_grammars]
	elif(grammar_name == "DC_LOC"):
		return [DC_LOC_grammar, DC_LOC_possible_tokens, DC_LOC_possible_grammars]		
	elif(grammar_name == "LISTA_ARG"):
		return [LISTA_ARG_grammar, LISTA_ARG_possible_tokens, LISTA_ARG_possible_grammars]
	elif(grammar_name == "ARGUMENTOS"):
		return [ARGUMENTOS_grammar, ARGUMENTOS_possible_tokens, ARGUMENTOS_possible_grammars]
	elif(grammar_name == "MAIS_IDENT"):
		return [MAIS_IDENT_grammar, MAIS_IDENT_possible_tokens, MAIS_IDENT_possible_grammars]
	elif(grammar_name == "PFALSA"):
		return [PFALSA_grammar, PFALSA_possible_tokens, PFALSA_possible_grammars]
	elif(grammar_name == "COMANDOS"):
		return [COMANDOS_grammar, COMANDOS_possible_tokens, COMANDOS_possible_grammars]
	elif(grammar_name == "CMD"):
		return [CMD_grammar, CMD_possible_tokens, CMD_possible_grammars]
	elif(grammar_name == "CONDICAO"):
		return [CONDICAO_grammar, CONDICAO_possible_tokens, CONDICAO_possible_grammars]
	elif(grammar_name == "RELACAO"):
		return [RELACAO_grammar, RELACAO_possible_tokens, RELACAO_possible_grammars]
	elif(grammar_name == "EXPRESSAO"):
		return [EXPRESSAO_grammar, EXPRESSAO_possible_tokens, EXPRESSAO_possible_grammars]
	elif(grammar_name == "OP_UN"):
		return [OP_UN_grammar, OP_UN_possible_tokens, OP_UN_possible_grammars]
	elif(grammar_name == "OUTROS_TERMOS"):
		return [OUTROS_TERMOS_grammar, OUTROS_TERMOS_possible_tokens, OUTROS_TERMOS_possible_grammars]
	elif(grammar_name == "OP_AD"):
		return [OP_AD_grammar, OP_AD_possible_tokens, OP_AD_possible_grammars]
	elif(grammar_name == "TERMO"):
		return [TERMO_grammar, TERMO_possible_tokens, TERMO_possible_grammars]
	elif(grammar_name == "MAIS_FATORES"):
		return [MAIS_FATORES_grammar, MAIS_FATORES_possible_tokens, MAIS_FATORES_possible_grammars]
	elif(grammar_name == "OP_MUL"):
		return [OP_MUL_grammar, OP_MUL_possible_tokens, OP_MUL_possible_grammars]
	elif(grammar_name == "FATOR"):
		return [FATOR_grammar, FATOR_possible_tokens, FATOR_possible_grammars]
	else:
		return None


# import tracemalloc
# tracemalloc.start()

testTokens = [
	"program",
	"ident",
	"ponto_virgula",
	"var",
	"ident",
	"virgula",
	"ident",
	"dois_pontos",
	"integer",
	"ponto_virgula",
	"begin",
	"end",
	"ponto"
]

grammars = [
	"PROGRAMA"
]	

PROGRAMA_possible_tokens = [
	"program",
	"ident",
	";",
	"."
]

PROGRAMA_possible_grammars = [
	"CORPO"
]

PROGRAMA_grammar = [
	[1, 'error', 'error', 'error', 'error', 'error'],
	['error', 2, 'error', 'error', 'error', 'error'],
	['error', 'error', 3, 'error', 'error', 'error'],
	['error', 'error', 'error', 'error', 4, 'error'],
	['error', 'error', 'error', 'success', 'error', 'error'],
]

CORPO_possible_tokens = [
	"begin",
	"end"
]

CORPO_possible_grammars = [
	"DC",
	"COMANDOS"
]

CORPO_grammar = [
	['error', 'error', 1, 'error', 'error'],
	[2, 'error', 'error', 'error', 'error'],
	['error', 'error', 'error', 3, 'error'],
	['error', 'success', 'error', 'error', 'error']
]

DC_possible_tokens = [
]

DC_possible_grammars = [
	"DC_V",
	"DC_P"
]

DC_grammar = [
	[1, 'error', 'error'],
	['error', 'success', 'error']
]

DC_V_possible_tokens = [
	"var",
	":",
	";"
]

DC_V_possible_grammars = [
	"VARIAVEIS",
	"TIPO_VAR",
	"DC_V"
]

DC_V_grammar = [
	[1, 'error', 'error', 'error', 'error', 'error', 'success'],
	['error', 'error', 'error', 2, 'error', 'error', 'error'],
	['error', 3, 'error', 'error', 'error', 'error', 'error'],
	['error', 'error', 'error', 'error', 4, 'error', 'error'],
	['error', 'error', 5, 'error', 'error', 'error', 'error'],
	['error', 'error', 'error', 'error', 'error', 'success', 'error']
]

TIPO_VAR_possible_tokens = [
	"real",
	"integer"
]

TIPO_VAR_possible_grammars = [
]

TIPO_VAR_grammar = [
	['success', 'success', 'error']
]

VARIAVEIS_possible_tokens = [
	"ident"
]

VARIAVEIS_possible_grammars = [
	"MAIS_VAR"
]

VARIAVEIS_grammar = [
	[1, 'error', 'error'],
	['error', 'success', 'error']
]

MAIS_VAR_possible_tokens = [
	","
]

MAIS_VAR_possible_grammars = [
	"VARIAVEIS"
]

MAIS_VAR_grammar = [
	[1, 'error', 'success'],
	['error', 'success', 'error']
]

DC_P_possible_tokens = [
	"procedure",
	"ident",
	";"
]

DC_P_possible_grammars = [
	"PARAMETROS",
	"CORPO_P",
	"DC_P"
]

DC_P_grammar = [
	[1, 'error', 'error', 'error', 'error', 'error', 'success'],
	['error', 2, 'error', 'error', 'error', 'error', 'error'],
	['error', 'error', 'error', 3, 'error', 'error', 'error'],
	['error', 'error', 4, 'error', 'error', 'error', 'error'],
	['error', 'error', 'error', 'error', 5, 'error', 'error'],
	['error', 'error', 'error', 'error', 'error', 'success', 'error']
]

PARAMETROS_possible_tokens = [
	"(",
	")"
]

PARAMETROS_possible_grammars = [
	"LISTA_PAR"
]

PARAMETROS_grammar = [
	[1, 'error', 'error', 'success'],
	['error', 'error', 2, 'error'],
	['error', 'success', 'error', 'error']
]

LISTA_PAR_possible_tokens = [
	":"
]

LISTA_PAR_possible_grammars = [
	"VARIAVEIS",
	"TIPO_VAR",
	"MAIS_PAR"
]

LISTA_PAR_grammar = [
	['error', 1, 'error', 'error', 'error'],
	[2, 'error', 'error', 'error', 'error'],
	['error', 'error', 3, 'error', 'error'],
	['error', 'error', 'error', 'success', 'error']
]

MAIS_PAR_possible_tokens = [
	";"
]

MAIS_PAR_possible_grammars = [
	"LISTA_PAR"
]

MAIS_PAR_grammar = [
	[1, 'error', 'success'],
	['error', 'success',  'error']
]

CORPO_P_possible_tokens = [
	"begin",
	"end",
	";"
]

CORPO_P_possible_grammars = [
	"DC_LOC",
	"COMANDOS"
]

CORPO_P_grammar = [
	['error', 'error', 'error', 1, 'error', 'error'],
	[2, 'error', 'error', 'error', 'error', 'error'],
	['error', 'error', 'error', 'error', 3, 'error'],
	['error', 4, 'error', 'error', 'error', 'error'],
	['error', 'error', 'success', 'error', 'error', 'error']
]

DC_LOC_possible_tokens = [
]

DC_LOC_possible_grammars = [
	"DC_V"
]

DC_LOC_grammar = [
	['success', 'error']
]

LISTA_ARG_possible_tokens = [
	"(",
	")"
]

LISTA_ARG_possible_grammars = [
	"ARGUMENTOS"
]

LISTA_ARG_grammar = [
	[1, 'error', 'error', 'success'],
	['error', 'error', 2, 'error'],
	['error', 'success', 'error', 'error']
]

ARGUMENTOS_possible_tokens = [
	"ident"
]

ARGUMENTOS_possible_grammars = [
	"MAIS_IDENT"
]

ARGUMENTOS_grammar = [
	[1, 'error', 'error'],
	['error', 'success', 'error']
]

MAIS_IDENT_possible_tokens = [
	";"
]

MAIS_IDENT_possible_grammars = [
	"ARGUMENTOS"
]

MAIS_IDENT_grammar = [
	[1, 'error', 'success'],
	['error', 'success', 'error']
]

PFALSA_possible_tokens = [
	"else"
]

PFALSA_possible_grammars = [
	"CMD"
]

PFALSA_grammar = [
	[1, 'error', 'success'],
	['error', 'success', 'error']
]

COMANDOS_possible_tokens = [
	";"
]

COMANDOS_possible_grammars = [
	"CMD",
	"COMANDOS"
]

COMANDOS_grammar = [
	['error', 1, 'error', 'success'],
	[2, 'error', 'error', 'error'],
	['error', 'error', 'success', 'error']
]

CMD_possible_tokens = [
	"(",
	")",
	"read",
	"write",
	"while",
	"do",
	"if",
	"then",
	"ident",
	":=",
	"begin",
	"end"
]

CMD_possible_grammars = [
	"VARIAVEIS",
	"CONDICAO",
	"CMD",
	"PFALSA",
	"EXPRESSAO",
	"LISTA_ARG",
	"COMANDOS"
]

CMD_grammar = [
 ['error', 'error', 1, 1, 4, 'error', 7, 'error', 11, 'error', 13, 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error'],
 [2, 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 3, 'error', 'error', 'error', 'error', 'error', 'error', 'error'],
 ['error', 'success', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 5, 'error', 'error', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 6, 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'success', 'error', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 8, 'error', 'error', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 9, 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 10, 'error', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'success', 'error', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 12, 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'success', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'success', 'error', 'error', 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 14, 'error'],
 ['error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'success', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error']
]

CONDICAO_possible_tokens = [
]

CONDICAO_possible_grammars = [
	"EXPRESSAO",
	"RELACAO"
]

CONDICAO_grammar = [
	[1, 'error', 'error'],
	['error', 2, 'error'],
	['success', 'error', 'error']
]

RELACAO_possible_tokens = [
	"=",
	"<>",
	">=",
	"<=",
	">",
	"<"
]

RELACAO_possible_grammars = [
]

RELACAO_grammar = [
	['success', 'success', 'success', 'success', 'success', 'success', 'error'],
]

EXPRESSAO_possible_tokens = [
]

EXPRESSAO_possible_grammars = [
	"TERMO",
	"OUTROS_TERMOS"
]

EXPRESSAO_grammar = [
	[1, 'error', 'error'],
	['error', 'success', 'error'],
]

OP_UN_possible_tokens = [
	"+",
	"-"
]

OP_UN_possible_grammars = [
]

OP_UN_grammar = [
	['success', 'success', 'success'],
]

OUTROS_TERMOS_possible_tokens = [
]

OUTROS_TERMOS_possible_grammars = [
	"OP_AD",
	"TERMO",
	"OUTROS_TERMOS"
]

OUTROS_TERMOS_grammar = [
	[1, 'error', 'error', 'success'],
	['error', 2, 'error', 'error'],
	['error', 'error', 'success', 'error'],
]

OP_AD_possible_tokens = [
	"+",
	"-"
]

OP_AD_possible_grammars = [
]

OP_AD_grammar = [
	['success', 'success', 'error'],
]

TERMO_possible_tokens = [
]

TERMO_possible_grammars = [
	"OP_UN",
	"FATOR",
	"MAIS_FATORES"
]

TERMO_grammar = [
	[1, 'error', 'error', 'error'],
	['error', 2, 'error', 'error'],
	['error', 'error', 'success', 'error'],
]

MAIS_FATORES_possible_tokens = [
]

MAIS_FATORES_possible_grammars = [
	"OP_MUL",
	"FATOR",
	"MAIS_FATORES"
]

MAIS_FATORES_grammar = [
	[1, 'error', 'error', 'success'],
	['error', 2, 'error', 'error'],
	['error', 'error', 'success', 'error'],
]

OP_MUL_possible_tokens = [
	"*",
	"/"
]

OP_MUL_possible_grammars = [
]

OP_MUL_grammar = [
	['success', 'success', 'error'],
]

FATOR_possible_tokens = [
	"(",
	")",
	"ident",
	"numero_int",
	"numero_real"
]

FATOR_possible_grammars = [
	"EXPRESSAO"
]

FATOR_grammar = [
	[1, 'error', 'success', 'success', 'success', 'error', 'error'],
	['error', 'error', 'error', 'error', 'error', 2, 'error'],
	['error', 'success', 'error', 'error', 'error', 'error', 'error'],
]

alias = [
"INICIAL",
"IDENT",
"NUMERO_INT",
"ERRO_REAL",
"NUMERO_REAL",
".",
";",
":",
":=",
",",
"(",
")",
"=",
"<",
"<>",
"<=",
">",
">=",
"+",
"-",
"*",
"/",
"ERRO_LEXICO"
]

alias = [x.lower() for x in alias]

states = [[0, 2, 1, 5, 6, 7, 9, 10, 11, 12, 13, 16, 18, 19, 20, 21, 22],
	   	  [0, 1, 1, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 2, 0, 3, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 4, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 4, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  8,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0, 15,  0, 14,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0, 17,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
          [0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0]
]

file1 = open("code.txt","r")
code = file1.read().rstrip()

def changeCode(new_code):
	code = new_code

# code = removeComments()
# print(code)

# index_2 = 0
# while(index_2 != len(code)):
# 	token = getNextToken(index_2)
# 	print(token)
# 	index_2 = token[1]

# parser()
# print(grammarDecoder('Z'))
# parserTest()

if(len(code) > 0):
	error_list = parser()
	# print(error_list)
	# codes = [code]
	# initial_code = code
	# old_code = code
	# error_traceback = []

	# if(error_list != None):
	# 	for i, error in enumerate(error_list):
	# 		error_list[i] = [error[0], error[1], error[2], error[3], error[4], error[5], error[6], i, 0, 0]

	# 	winner = 0
	# 	level = 0
	# 	last_index = len(error_list) - 1
	# 	for i, error in enumerate(error_list):
	# 		last_one = False
	# 		if(i == last_index):
	# 			last_one = True

	# 		code = codes[error[-1]]
	# 		code = putBeforeToken(error[0], error[3], error[4])
	# 		codes.append(code)
	# 		code_id = len(codes) - 1
	# 		new_error_list = parser()
	# 		if(new_error_list != None):

	# 			for k, new_error in enumerate(new_error_list):
	# 				error_list.append([new_error[0], new_error[1], new_error[2], new_error[3], new_error[4], new_error[5], new_error[6], error[7], level, code_id])

	# 			code = codes[error[-1]]
	# 			code = replaceToken(error[0], error[3], error[4])
	# 			codes.append(code)
	# 			code_id = len(codes) - 1
	# 			new_error_list = parser()
	# 			if(new_error_list != None):
	# 				for k, new_error in enumerate(new_error_list):
	# 					error_list.append([new_error[0], new_error[1], new_error[2], new_error[3], new_error[4], new_error[5], new_error[6], error[7], level, code_id])

	# 				if(last_one):

	# 					level += 1
	# 					last_one = False
	# 					last_index = len(error_list) - 1

	# 			else:

	# 				winner = i
	# 				del error_list[i+1:]

	# 				error_winner = error_list[i]
	# 				for error in error_list:
	# 					if(error[-3] == error_winner[-3]):
	# 						error_traceback.append(error)

	# 				break
				

	# 		else:
	# 			winner = i
	# 			del error_list[i+1:]

	# 			error_winner = error_list[i]
	# 			for error in error_list:
	# 				if(error[-3] == error_winner[-3]):
	# 					error_traceback.append(error)

	# 			break



		


	# print(error_traceback)


	
	# print(code)

else:

	print("\nFail, empty code.\n")

# if('1'=='1'):
# 	print('a')
# newCode(';', 'begin',57 - 1)

# current, peak = tracemalloc.get_traced_memory()
# print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
# tracemalloc.stop()
 