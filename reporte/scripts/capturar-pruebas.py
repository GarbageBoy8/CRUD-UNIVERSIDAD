#!/usr/bin/env python3
"""Ejecuta Postman CLI y captura su resultado real en una terminal Kitty X11."""
from pathlib import Path
import json, os, subprocess, time, textwrap, sys, re
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8031'
state={}; results=[]

def short_json(value):
    if isinstance(value,dict):
        return json.dumps(value,ensure_ascii=False,indent=2)
    return str(value)

def test(number,title,method,path,expected,body=None,auth=True,checks='',save=None):
    path=path.format(**state)
    key=f'{number:02d}'
    raw=Path('/tmp')/f'lumbre-postman-{key}.json'
    cmd=['postman','request',method,BASE+path,'--no-report-events','--timeout','15000','--output',str(raw)]
    shown=f'$ postman request {method} "{BASE+path}"'
    if body is not None:
        body={k:(v.format(**state) if isinstance(v,str) else v) for k,v in body.items()}
        payload=ROOT/'datos'/f'{key}-peticion.json'
        payload.write_text(json.dumps(body,ensure_ascii=False,indent=2))
        cmd+=['--header','Content-Type:application/json','--body',json.dumps(body,ensure_ascii=False)]
        shown+=f'\n  --body "$(cat datos/{key}-peticion.json)"'
    if auth:
        token=Path('/tmp/lumbre-reporte-expirado-8031.txt').read_text() if auth=='expired' else ('invalido' if auth=='invalid' else state['token'])
        cmd+=['--auth-bearer-token',token]
        shown+='\n  --auth-bearer-token "$TOKEN"'
    script=f"pm.test('HTTP {expected}', () => pm.response.to.have.status({expected}));"+checks
    cmd+=['--script-post-request',script]
    started=time.time()
    process=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
    if not raw.exists():raise RuntimeError(process.stdout+process.stderr)
    data=json.loads(raw.read_text());response=json.loads(data['response']['body'])
    if save:state[save]=response['datos']['_id']
    if number==3 or title=='Renovar acceso para pruebas negativas':state['token']=response['token']
    public=json.loads(json.dumps(data))
    if 'token' in response:
        response['token']=response['token'][:20]+'... [oculto por seguridad]'
    public['response']['body']=json.dumps(response,ensure_ascii=False)
    for header in public['request'].get('header',[]):
        if header.get('key','').lower()=='authorization':header['value']='Bearer [TOKEN OCULTO]'
    if number==3 or title=='Renovar acceso para pruebas negativas':
        public['request']['body']='{"usuario":"practica","contrasena":"[OCULTA]"}'
    public=json.loads(re.sub(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', '[TOKEN OCULTO]', json.dumps(public,ensure_ascii=False)))
    (ROOT/'datos'/f'{key}-resultado.json').write_text(json.dumps(public,ensure_ascii=False,indent=2))
    record={'numero':number,'titulo':title,'metodo':method,'ruta':path,'esperado':expected,'estado':data['response']['code'],'duracion_ms':data['response']['responseTime'],'pruebas':data.get('tests',{}),'respuesta':response,'peticion':body,'archivo':f'evidencias/{key}.png','timestamp':data['timestamp'],'exit_code':process.returncode,'checks':checks,'base_url':BASE,'auth':auth,'save':save}
    if number==3 or title=='Renovar acceso para pruebas negativas':record['peticion']['contrasena']='[OCULTA]'
    results.append(record)
    (ROOT/'datos'/'resultados.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print('\033[2J\033[H',end='')
    print('\033[1;36mPOSTMAN CLI  |  EJERCICIO CRUD — LUMBRE\033[0m')
    print(f'PRUEBA {key} · {title}\n')
    for line in shown.splitlines():
        print('\033[33m'+textwrap.fill(line,width=min(95,os.get_terminal_size().columns-2),subsequent_indent='  ')+'\033[0m')
    print('\n\033[1mRESPUESTA HTTP '+str(record['estado'])+' '+data['response']['status']+f"  |  {record['duracion_ms']} ms\033[0m")
    print('Content-Type: application/json\n')
    # Se mantiene el cuerpo completo; solo se compacta el formato JSON para la captura.
    def pretty(obj, depth=0):
        if depth >= 1 or not isinstance(obj,(dict,list)):
            return json.dumps(obj,ensure_ascii=False)
        indent='  '*depth
        if isinstance(obj,dict):
            return '{\n'+',\n'.join(indent+'  '+json.dumps(k,ensure_ascii=False)+': '+pretty(v,depth+1) for k,v in obj.items())+'\n'+indent+'}'
        return json.dumps(obj,ensure_ascii=False)
    visible=response
    if number==50:
        visible={**response, 'datos':response['datos'][:2]}
        print('Vista de los primeros 2 resultados; JSON íntegro en datos/50-resultado.json')
    if number==51 and len(response['datos']['resumen'])>650:
        visible={'datos':{**response['datos'],'resumen':response['datos']['resumen'][:650]+'...'}}
        print('Resumen abreviado para captura; JSON íntegro en datos/51-resultado.json')
    for line in pretty(visible).splitlines():
        print(textwrap.fill(line,width=min(95,os.get_terminal_size().columns-2),subsequent_indent='    ',replace_whitespace=False,drop_whitespace=False))
    tests=data.get('tests',{})
    print(f"\n\033[1;32mASERCIONES: {tests.get('passed',0)} aprobadas / {tests.get('total',0)} ejecutadas\033[0m")
    print('Cliente: Postman CLI · JSON formateado · Token oculto cuando corresponde',flush=True)
    time.sleep(.7)
    subprocess.run(['import','-window','Pruebas API Lumbre',str(ROOT/'evidencias'/f'{key}.png')],check=True)
    assert record['estado']==expected,(title,record['estado'],response)
    # Postman CLI 1.74 retorna 1 ante HTTP 4xx incluso con aserciones aprobadas.
    assert process.returncode in ([0,1] if expected >= 400 else [0]),(title,process.stdout,process.stderr)
    assert tests.get('failed',0)==0
    print(f'Captura {key} guardada.',flush=True)

schema="pm.test('Respuesta JSON',()=>pm.expect(pm.response.headers.get('Content-Type')).to.include('application/json'));"

def ejecutar_local():
    test(1,'Consultar los recursos de la API','GET','/api',200,auth=False,checks=schema)
    test(2,'Rechazar una contraseña incorrecta','POST','/auth/login',401,{'usuario':'practica','contrasena':'incorrecta'},False,checks=schema)
    test(3,'Obtener el token JWT de acceso','POST','/auth/login',200,{'usuario':'practica','contrasena':'PracticaCRUD2026!'},False,checks="pm.test('Token recibido',()=>pm.expect(pm.response.json().token).to.be.a('string'));")
    test(4,'Rechazar una petición sin token','GET','/libros/obtenerVarios',401,auth=False,checks=schema)
    test(5,'Rechazar un token vencido','GET','/generos/obtenerVarios',403,auth='expired',checks=schema)
    test(6,'Crear un género literario','POST','/generos/falta',201,{'nombre':'Tecnología','descripcion':'Libros sobre programación y sistemas.'},checks="pm.test('Género guardado',()=>pm.expect(pm.response.json().datos.nombre).to.eql('Tecnología'));",save='genero')
    test(7,'Consultar todos los géneros','GET','/generos/obtenerVarios',200,checks="pm.test('Un género registrado',()=>pm.expect(pm.response.json().datos).to.have.lengthOf(1));")
    test(8,'Consultar un género por ID','GET','/generos/obtenerUno/{genero}',200,checks="pm.test('Nombre esperado',()=>pm.expect(pm.response.json().datos.nombre).to.eql('Tecnología'));")
    test(9,'Actualizar un género','PUT','/generos/baja/{genero}',200,{'nombre':'Informática','descripcion':'Programación, bases de datos y redes.'},checks="pm.test('Nombre actualizado',()=>pm.expect(pm.response.json().datos.nombre).to.eql('Informática'));")
    test(10,'Crear un libro vinculado al género','POST','/libros/falta',201,{'nombre':'Fundamentos de APIs REST','autor':'Ana Torres','genero':'{genero}','ubicacion':'A-01','ejemplares':3},checks="pm.test('Relación poblada',()=>pm.expect(pm.response.json().datos.genero.nombre).to.eql('Informática'));",save='libro')
    test(11,'Consultar el catálogo de libros','GET','/libros/obtenerVarios',200,checks="pm.test('Un libro registrado',()=>pm.expect(pm.response.json().datos).to.have.lengthOf(1));")
    test(12,'Consultar un libro por ID','GET','/libros/obtenerUno/{libro}',200,checks="pm.test('Autor esperado',()=>pm.expect(pm.response.json().datos.autor).to.eql('Ana Torres'));")
    test(13,'Actualizar estante y ejemplares','PUT','/libros/baja/{libro}',200,{'ubicacion':'B-02','ejemplares':5},checks="pm.test('Cambios guardados',()=>{pm.expect(pm.response.json().datos.ubicacion).to.eql('B-02');pm.expect(pm.response.json().datos.ejemplares).to.eql(5);});")
    test(14,'Proteger un género con libros asociados','DELETE','/generos/eliminar/{genero}',400,checks="pm.test('Explica la referencia',()=>pm.expect(pm.response.json().mensaje).to.include('asociado'));")
    test(15,'Rechazar ejemplares negativos','PUT','/libros/baja/{libro}',400,{'ejemplares':-2},checks=schema)
    test(16,'Rechazar un ID con formato inválido','GET','/libros/obtenerUno/id-invalido',400,checks=schema)
    test(17,'Eliminar un libro','DELETE','/libros/eliminar/{libro}',200,checks="pm.test('Devuelve el registro eliminado',()=>pm.expect(pm.response.json().datos.nombre).to.eql('Fundamentos de APIs REST'));")
    test(18,'Comprobar que el libro ya no existe','GET','/libros/obtenerUno/{libro}',404,checks=schema)
    test(19,'Eliminar el género sin libros asociados','DELETE','/generos/eliminar/{genero}',200,checks=schema)
    test(20,'Comprobar el catálogo vacío','GET','/libros/obtenerVarios',200,checks="pm.test('No quedan libros',()=>pm.expect(pm.response.json().datos).to.have.lengthOf(0));")
    test(21,'Comprobar la eliminación del género','GET','/generos/obtenerUno/{genero}',404,checks=schema)
    print('\nTodas las pruebas locales se completaron. Evidencias guardadas.',flush=True)
    time.sleep(1)

def ejecutar_externo():
    global BASE, results
    BASE='http://127.0.0.1:8032'
    results=json.loads((ROOT/'datos'/'resultados.json').read_text())
    test(22,'Buscar obras: Open Library SIMULADO','GET','/servicios/libros?q=fox',200,auth=False,checks="pm.test('Obra adaptada',()=>pm.expect(pm.response.json().datos[0].nombre).to.eql('Fantastic Mr. Fox'));")
    test(23,'Consultar ficha: proveedor SIMULADO','GET','/servicios/libros/OL45804W',200,auth=False,checks="pm.test('Descripción opcional',()=>pm.expect(pm.response.json().datos.resumen).to.include('no tiene una descripción'));")
    test(24,'Obra inexistente: proveedor SIMULADO','GET','/servicios/libros/OL999999W',404,auth=False,checks=schema)
    test(25,'Falla del proveedor: respuesta 502','GET','/servicios/libros?q=upstream-error',502,auth=False,checks="pm.test('Error controlado',()=>pm.expect(pm.response.json().mensaje).to.include('no está disponible'));")
    time.sleep(1)

def ejecutar_complemento():
    global results
    results=json.loads((ROOT/'datos'/'resultados.json').read_text())[:25]
    test(26,'Renovar acceso para pruebas negativas','POST','/auth/login',200,{'usuario':'practica','contrasena':'PracticaCRUD2026!'},False,checks="pm.test('Token recibido',()=>pm.expect(pm.response.json().token).to.be.a('string'));")
    test(27,'Login sin campos requeridos','POST','/auth/login',400,{},False,checks=schema)
    test(28,'Token inválido en consulta general','GET','/generos/obtenerVarios',401,auth='invalid',checks=schema)
    test(29,'Alta de género sin nombre','POST','/generos/falta',400,{'descripcion':'Falta nombre'},checks=schema)
    test(30,'Crear género para validar conflictos','POST','/generos/falta',201,{'nombre':'Ensayo'},checks="pm.test('Nombre guardado',()=>pm.expect(pm.response.json().datos.nombre).to.eql('Ensayo'));",save='genero')
    test(31,'Alta de género duplicado','POST','/generos/falta',400,{'nombre':'Ensayo'},checks=schema)
    test(32,'Cambio de género con nombre vacío','PUT','/generos/baja/{genero}',400,{'nombre':''},checks=schema)
    test(33,'Crear segundo género','POST','/generos/falta',201,{'nombre':'Historia'},checks=schema,save='otro_genero')
    test(34,'Renombrado con nombre duplicado','PUT','/generos/baja/{otro_genero}',409,{'nombre':'Ensayo'},checks=schema)
    test(35,'Consulta de género con ID inválido','GET','/generos/obtenerUno/invalido',400,checks=schema)
    test(36,'Cambio de género inexistente','PUT','/generos/baja/000000000000000000000000',404,{'nombre':'No existe'},checks=schema)
    test(37,'Baja de género inexistente','DELETE','/generos/eliminar/000000000000000000000000',404,checks=schema)
    test(38,'Alta de libro sin autor','POST','/libros/falta',400,{'nombre':'Ensayos','genero':'{genero}','ubicacion':'C-01','ejemplares':1},checks=schema)
    test(39,'Alta de libro con género inexistente','POST','/libros/falta',400,{'nombre':'Ensayos','autor':'Autor de prueba','genero':'000000000000000000000000','ubicacion':'C-01','ejemplares':1},checks=schema)
    test(40,'Alta de libro con ejemplares fraccionarios','POST','/libros/falta',400,{'nombre':'Ensayos','autor':'Autor de prueba','genero':'{genero}','ubicacion':'C-01','ejemplares':1.5},checks=schema)
    test(41,'Cambio de libro inexistente','PUT','/libros/baja/000000000000000000000000',404,{'ejemplares':2},checks=schema)
    test(42,'Cambio de libro con campos no permitidos','PUT','/libros/baja/000000000000000000000000',400,{'propietario':'otro'},checks=schema)
    test(43,'Baja de libro inexistente','DELETE','/libros/eliminar/000000000000000000000000',404,checks=schema)
    test(44,'Baja de libro con ID inválido','DELETE','/libros/eliminar/invalido',400,checks=schema)
    test(45,'Eliminar género de control','DELETE','/generos/eliminar/{otro_genero}',200,checks=schema)
    test(46,'Eliminar género de pruebas negativas','DELETE','/generos/eliminar/{genero}',200,checks=schema)
    test(47,'Confirmar géneros vacíos','GET','/generos/obtenerVarios',200,checks="pm.test('Sin géneros',()=>pm.expect(pm.response.json().datos).to.have.lengthOf(0));")
    test(48,'Búsqueda externa con parámetro vacío','GET','/servicios/libros?q=',400,auth=False,checks=schema)
    test(49,'Detalle externo con ID inválido','GET','/servicios/libros/id-invalido',400,auth=False,checks=schema)
    test(50,'Buscar Pedro Páramo en Open Library REAL','GET','/servicios/libros?q=Pedro%20Paramo',200,auth=False,checks="pm.test('Datos bibliográficos reales',()=>{const r=pm.response.json();pm.expect(r.datos.length).to.be.above(0);pm.expect(r.datos[0]).to.have.all.keys('id','nombre','autor','anio');});")
    test(51,'Consultar obra en Open Library REAL','GET','/servicios/libros/OL1731119W',200,auth=False,checks="pm.test('Ficha real',()=>{const d=pm.response.json().datos;pm.expect(d.id).to.eql('OL1731119W');pm.expect(d.nombre).to.include('Pedro');});")
    time.sleep(1)

if __name__ == '__main__':
    if '--externo' in sys.argv: ejecutar_externo()
    elif '--complemento' in sys.argv: ejecutar_complemento()
    else: ejecutar_local()
