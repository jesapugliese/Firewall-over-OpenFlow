# Firewall-over-OpenFlow

# Cómo ejecutar el programa

Utilizamos Docker que ya incluye todo el ambiente necesario para poder ejecutarlo. Sólo necestamos externo a docker el ovs.

# Externo a docker

Sólo se debe de tener en la máquina donde se utilice: ovs

# Cómo instalar ovs

```python
sudo apt update
sudo apt install openvswitch-switch
```

### **Iniciar OVS**

```bash
sudo service openvswitch-switch start
```

> Verificá que esté funcionando:
> 

```bash
sudo ovs-vsctl show
```

Deberías ver la version de ovs:

```
ovs_version: "2.17.1"
```

# Terminal 1:

parado donde esté el Dockerfile

```jsx
docker build -t firewall-mininet .
```

```jsx
docker run -it --rm --privileged --net=host firewall-mininet
```

### Dentro del contenedor: Levantar el controlador

En una terminal dentro del contenedor:

### Corre el controlador POX con tu firewall

```bash
cd /pox
```

```jsx
python pox.py forwarding.l2_learning firewall
```

# Terminal 2

```jsx
docker run -it --rm   --privileged   --net=host   -v /var/run/openvswitch:/var/run/openvswitch   firewall-mininet
```

Levantar la topología una vez que ya esé corriendo el firefox.

```python
mn --custom /pox/ext/topology.py --topo topologia,switches_count=3 --mac --arp --switch ovsk --controller remote
```

---

# Nuestros hosts

Topología que se puede ver desde Mininet ejecutando `links`

<Host host1: host1-eth0:10.0.0.1 pid=25>
<Host host2: host2-eth0:10.0.0.2 pid=27>
<Host host3: host3-eth0:10.0.0.3 pid=29>
<Host host4: host4-eth0:10.0.0.4 pid=31>

# Cumplimiento de Reglas

Se pueden probar de la siguiente manera:

## Regla 1 Descartar mensajes con puerto destino 80

UDP:

```python
host4 iperf -u -s -p 80 &
host1 iperf -u -c host4 -p 80
```

TCP:

```python
host4 iperf -s -p 80 &
host1 iperf -c host4 -p 80
```

Lo siguiente no se podría por la regla 3

```python
host2 iperf -u -s -p 80 &
host4 iperf -u -c host2 -p 80
```

```python
host4 iperf -u -s -p 80 &
host2 iperf -u -c host4 -p 80
```

## Regla 2:

Se deben descartar todos los mensajes que provengan del host 1, tengan como puerto destino el 5001, y esten utilizando el protocolo UDP

```python
host4 iperf -u -s -p 5001 &
host1 iperf -u -c host4 -p 5001
```

## Regla 3: h2 y h4 no se comunican

Dos hosts no se pueden comunicar.

Elegimos host2 y host4

UDP

```python
host4 iperf -u -s -p 12345 &
host2 iperf -u -c host4 -p 12345
```

TCP

```python
host4 iperf -s -p 12345 &
host2 iperf -c host4 -p 12345
```

Debe funcionar en ambas direcciones.

UDP

```python
host2 iperf -u -s -p 12345 &
host4 iperf -u -c host2 -p 12345
```

TCP

```python
host2 iperf -u -s -p 12345 &
host4 iperf -u -c host2 -p 12345
```

## Caso felíz

```python
host4 iperf -u -s -p 12345 &
host1 iperf -u -c host4 -p 12345
```
