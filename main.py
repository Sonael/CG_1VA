import sys
import math
import pygame


# Configurações

RESX = 512          # resolução horizontal da tela
RESY = 512          # resolução vertical da tela
ARQ_OBJETO = "objetos/calice2.byu"    # malha de triangulos
ARQ_CAMERA = "camera.txt"    # parametros da camera virtual

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)



# Operações vetoriais basicas

def subtrair(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def escalar(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def produto_interno(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def produto_vetorial(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def norma(a):
    return math.sqrt(produto_interno(a, a))


def normalizar(a):
    n = norma(a)
    if n == 0:
        return (0.0, 0.0, 0.0)
    return (a[0] / n, a[1] / n, a[2] / n)



# Carregando vertices e triangulos da malha

def carregar_objeto(caminho):

    with open(caminho, "r") as f:
        numeros = f.read().split()

    pos = 0
    n_vertices = int(numeros[pos]); pos += 1
    n_triangulos = int(numeros[pos]); pos += 1

    vertices = []
    for _ in range(n_vertices):
        x = float(numeros[pos]); pos += 1
        y = float(numeros[pos]); pos += 1
        z = float(numeros[pos]); pos += 1
        vertices.append((x, y, z))

    triangulos = []
    for _ in range(n_triangulos):
        a = int(numeros[pos]); pos += 1
        b = int(numeros[pos]); pos += 1
        c = int(numeros[pos]); pos += 1
        # Convertendo indices para comecar em 0
        triangulos.append((a - 1, b - 1, c - 1))

    return vertices, triangulos



# 3. Carregando os parametros de camera

def carregar_camera(caminho):

    params = {}
    with open(caminho, "r") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            # separando a linha por chave / valores
            linha = linha.replace("=", " ")
            partes = linha.split()
            chave = partes[0]
            valores = [float(v) for v in partes[1:]]
            params[chave] = valores

    N = tuple(params["N"])
    V = tuple(params["V"])
    d = params["d"][0]
    hx = params["hx"][0]
    hy = params["hy"][0]
    C = tuple(params["C"])
    return N, V, d, hx, hy, C



# Base ortonormal do sistema de vista {U, V, N}

def calcular_base(N, V):
    
    # Ortogonalizar V:  V' = V - (<V,N>/<N,N>) * N
    fator = produto_interno(V, N) / produto_interno(N, N)
    Vlinha = subtrair(V, escalar(N, fator))

    # Normalizar V' e N
    Nn = normalizar(N)
    Vn = normalizar(Vlinha)

    # Calcular U = N x V' e normalizar
    U = normalizar(produto_vetorial(Nn, Vn))

    return U, Vn, Nn



# 4. Mudança de coordenadas: mundo | vista

def mundo_para_vista(P, U, V, N, C):
    
    t = subtrair(P, C)
    xv = produto_interno(U, t)
    yv = produto_interno(V, t)
    zv = produto_interno(N, t)
    return (xv, yv, zv)


# 5. Projeção em perspectiva | normalizadas | tela

def projetar(ponto_vista, d, hx, hy):

    xv, yv, zv = ponto_vista
    if zv <= 0:
        return None
    
    xsn = (d / hx) * (xv / zv)
    ysn = (d / hy) * (yv / zv)
    return (xsn, ysn)


def para_tela(coord_norm):
    
    xsn, ysn = coord_norm
    i = math.floor(((xsn + 1) / 2) * RESX + 0.5)
    j = math.floor(RESY - ((ysn + 1) / 2) * RESY + 0.5)
    return (i, j)



# Rasterizacao de triangulos - scan line

def pintar_triangulo(tela, p0, p1, p2, cor):

    pts = [p0, p1, p2]

    # limites verticais do triangulo
    y_min = min(p[1] for p in pts)
    y_max = max(p[1] for p in pts)
    y_min = max(y_min, 0)
    y_max = min(y_max, RESY - 1)

    for y in range(y_min, y_max + 1):
        interseccoes = []

        for k in range(3):
            (xa, ya) = pts[k]
            (xb, yb) = pts[(k + 1) % 3]
            if ya == yb:
                continue
            if (ya <= y < yb) or (yb <= y < ya):
                x = xa + (y - ya) * (xb - xa) / (yb - ya)
                interseccoes.append(x)

        interseccoes.sort()
        
        for m in range(0, len(interseccoes) - 1, 2):
            x_ini = int(math.ceil(interseccoes[m]))
            x_fim = int(math.floor(interseccoes[m + 1]))
            x_ini = max(x_ini, 0)
            x_fim = min(x_fim, RESX - 1)
            for x in range(x_ini, x_fim + 1):
                tela.set_at((x, y), cor)



# Desenhando da cena

def desenhar(tela, vertices, triangulos, camera):
    N, V, d, hx, hy, C = camera
    U, Vn, Nn = calcular_base(N, V)

    tela.fill(PRETO)

    # convertendo todos os vertices para coordenadas de tela
    tela_coords = []
    for P in vertices:
        pv = mundo_para_vista(P, U, Vn, Nn, C)
        cn = projetar(pv, d, hx, hy)
        if cn is None:
            tela_coords.append(None)
        else:
            tela_coords.append(para_tela(cn))

    # preenchendo cada triangulo
    for (a, b, c) in triangulos:
        pa, pb, pc = tela_coords[a], tela_coords[b], tela_coords[c]
        if pa is None or pb is None or pc is None:
            continue  # alguns vertices atras da camera
        pintar_triangulo(tela, pa, pb, pc, BRANCO)



# Programa principal

def main():
    # abrindo arquivo da pasta objetos
    arq_objeto = sys.argv[1] if len(sys.argv) > 1 else ARQ_OBJETO

    pygame.init()
    tela = pygame.display.set_mode((RESX, RESY))
    pygame.display.set_caption("Projeto 1a VA (R: recarregar camera | ESC: sair)")

    vertices, triangulos = carregar_objeto(arq_objeto)
    camera = carregar_camera(ARQ_CAMERA)
    desenhar(tela, vertices, triangulos, camera)
    pygame.display.flip()

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_r:
                    # recarrega camera do arquivo e redesenha o objeto
                    camera = carregar_camera(ARQ_CAMERA)
                    desenhar(tela, vertices, triangulos, camera)
                    pygame.display.flip()
                    print("Parametros de camera recarregados.")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
