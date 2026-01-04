# STAER - Sistema de Visualização de Radar Secundário

Este projeto foi desenvolvido no âmbito da unidade curricular de STAER. O objetivo é a criação de um sistema capaz de recolher, tratar, armazenar e visualizar informação de tráfego aéreo proveniente de radares secundários (SSR) e receptores ADS-B (Modo S).

## 🚀 Funcionalidades

* **Recolha de Dados:** Script automático que consome dados JSON de fontes `dump1090`.
* **Persistência:** Armazenamento histórico em base de dados SQLite.
* **Visualização Geográfica:** Mapa interativo (OpenStreetMap) focado na zona do Porto.
* **Filtragem Dinâmica:** Filtros para zona geográfica e estado da aeronave (Solo/Voo).
* **Tempo Real:** Atualização automática da interface a cada 10 segundos.

---

## 🛠️ Instalação e Execução

Este projeto foi desenhado para correr em ambiente Linux (Debian/Ubuntu), idealmente num contentor **Proxmox**.

### Pré-requisitos
```bash
sudo apt update
sudo apt install python3-pip python3-venv git -y