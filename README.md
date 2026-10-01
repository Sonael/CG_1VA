# Computação Gráfica Básica 1ª VA

Carrega uma malha de triângulos 3D de um arquivo de texto, faz a projeção em
perspectiva dos vértices e preenche os triângulos com o algoritmo de
rasterização **scan line** (varredura). Pixels dos triângulos ficam brancos e
o fundo preto.

## Arquivos

| Arquivo       | Descrição                                                      |
|---------------|----------------------------------------------------------------|
| `main.py`     | Programa principal (todo o pipeline das aulas 08 e 09).        |
| `camera.txt`  | Parâmetros da câmera virtual (N, V, d, hx, hy, C).             |
| `objetos/`    | Malhas de triângulos (formato `.byu`, igual ao da spec).       |

Objetos disponíveis em `objetos/`: `calice2.byu`, `maca.byu`, `maca2.byu`,
`vaso.byu`, `piramide.byu`, `triangulo.byu`.

## Como executar

```bash
python main.py                       # usa o objeto padrao (objetos/calice2.byu)
python main.py objetos/vaso.byu      # carrega qualquer malha passada como argumento
```

- **R** - recarrega os parâmetros da câmera do arquivo `camera.txt` e redesenha
  (permite alterar a câmera sem fechar o programa).
- **ESC** - sair.


## Pipeline

1. Carregar vértices e triângulos (`carregar_objeto`).
2. Carregar parâmetros de câmera (`carregar_camera`).
3. Base ortonormal do sistema de vista (`calcular_base`):
   - Ortogonalizar V (Gram-Schmidt): `V' = V - (⟨V,N⟩/⟨N,N⟩)·N`
   - Normalizar N e V'
   - `U = N × V'`
4. Mundo → vista: `[xv,yv,zv]ᵀ = [U;V;N]·(P−C)` (`mundo_para_vista`).
5. Perspectiva + normalizadas: `xsn = (d/hx)·(xv/zv)`, `ysn = (d/hy)·(yv/zv)` (`projetar`).
6. Coordenadas de tela: `i = ⌊((xsn+1)/2)·Resx + 0,5⌋`,
   `j = ⌊Resy − ((ysn+1)/2)·Resy + 0,5⌋` (`para_tela`).
7. Preenchimento por varredura (`pintar_triangulo`): para cada linha horizontal,
   acha as interseções com as arestas e pinta os pixels entre elas.
