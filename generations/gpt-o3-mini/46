# Código original não modificado...

# Seção modificada:
import math

def numeros_quatro_quadrados_nao_nulos(max_val):
    expressable_numbers = set()
    # Calcula o maior inteiro cuja raiz quadrada ao quadrado seja <= max_val
    max_root = int(math.sqrt(max_val))
    for a in range(1, max_root + 1):
        for b in range(1, max_root + 1):
            for c in range(1, max_root + 1):
                for d in range(1, max_root + 1):
                    soma = a*a + b*b + c*c + d*d
                    if soma <= max_val:
                        expressable_numbers.add(soma)
    return sorted(expressable_numbers)

if __name__ == "__main__":
    max_val = int(input("Digite o limite máximo: "))
    numeros = numeros_quatro_quadrados_nao_nulos(max_val)
    print("Números que podem ser expressos como a soma de quatro quadrados não nulos:")
    print(numeros)

# Restante do código original não modificado...
