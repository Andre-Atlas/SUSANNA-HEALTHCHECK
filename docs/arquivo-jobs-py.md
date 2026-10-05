# `jobs.py`

Implementa a fila FIFO que controla os trabalhos submetidos ao servidor. Limita a concorrência e a quantidade em espera, acompanha estado e etapa, permite cancelamento e encerra pedidos que excedem prazos ou perdem o cliente.

O servidor cria a fila e `app.js` acompanha os trabalhos pelos endpoints de jobs. O módulo também mede tempos por etapa e expõe métricas agregadas, sem registrar o texto das conversas.
