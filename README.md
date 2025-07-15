# Railway Job Bot - Configuración CRON

Para ejecutar el bot a las 8 AM y 8 PM VET (UTC-4):
- 8 AM VET = 12:00 PM UTC
- 8 PM VET = 12:00 AM UTC (medianoche)

## CRON Expression:
```
0 0,12 * * *
```

## Variables de entorno en Railway:
- EMAIL_FROM=jose.trader89@hotmail.com
- EMAIL_TO=jose.trader89@hotmail.com  
- APP_PASSWORD=bihxmgojvjhsploc

## Comando de ejecución:
```
python main.py
```

## Configuración en Railway:
1. Conectar repo de GitHub
2. Agregar variables de entorno
3. Configurar CRON job con la expresión: 0 0,12 * * *
4. Deploy automático
