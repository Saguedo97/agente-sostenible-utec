# Subir el proyecto a GitHub

## Antes de hacer `git add`

Nunca subas `.env`.

Comprueba:

```powershell
git status
Get-ChildItem -Force .env*
```

`.env` debe existir localmente, pero `.gitignore` debe impedir que aparezca como
archivo a commitear.

## Inicializar

```powershell
git init
git branch -M main
git add .
git status
git commit -m "Initial sustainable project agent"
```

Revisa `git status` antes del commit.

## Crear el repositorio remoto

Crea un repositorio vacío en GitHub, por ejemplo:

```text
agente-sostenible-utec
```

No marques "Add a README" si ya tienes este README.

Luego:

```powershell
git remote add origin https://github.com/TU_USUARIO/agente-sostenible-utec.git
git push -u origin main
```

## Datos e imágenes

Para revisión académica conviene incluir el código, README, Marco 2021, dataset
necesario para reproducir tests y una muestra representativa de imágenes.

Antes de subir muchos binarios revisa tamaños. Si algún archivo supera el límite
normal de GitHub, usa Git LFS o no lo incluyas en Git.

## Checklist de entrega

- [ ] `.env` NO está en Git
- [ ] `.env.example` SÍ está
- [ ] `python test_local.py` pasa
- [ ] al menos un `python main.py <CUI> --trace` fue probado
- [ ] README explica instalación
- [ ] ARCHITECTURE.md explica el diseño
- [ ] CODE_WALKTHROUGH.md explica los archivos
- [ ] el repositorio no contiene keys ni secretos
