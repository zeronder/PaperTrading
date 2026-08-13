from package import Client, default_correlation_id, default_mode, default_token_list
from package.logger import setup_logging, get_logger
from package.database import Database
from package.tick import Tick
import threading 
from queue import Queue, Empty


setup_logging()
logger = get_logger(__name__)
strategy_queue = Queue(maxsize=100000)
database_queue = Queue(maxsize=100000)

def database_worker():
    """
    consume ticks from queue and save them into database
    """
    logger.info("Database worker started")

    db = Database()

    batch = []
    BATCH_SIZE = 10
    BATCH_TIMEOUT = 2


    while True:
        
        try:
            tick = database_queue.get(timeout=BATCH_TIMEOUT)
            batch.append(tick)

            if len(batch)>=BATCH_SIZE:
                db.insert_ticks(batch)

                logger.debug(f"Database batch saved: {len(batch)} ticks")
                batch.clear()
            database_queue.task_done()

        except Empty:
            if batch:
                try:
                    db.insert_ticks(batch)
                    logger.debug(f"Database Timeout Flush: {len(batch)} ticks")  
                    batch.clear()
                except Exception:
                    logger.exception("Database timeout batch failed")

                

def strategy_worker():
    """
    Get Tick from strategy queue
    and process strategy
    """

    logger.info("Strategy worker started")

    while True:
        tick = strategy_queue.get()

        try:
            logger.debug(f"Strategy received tick: {tick.token}")
            # Example:
            #
            # signal = strategy.process(tick)
            #
            # if signal:
            #     order_manager.execute(signal)
        
        except Exception:
            logger.exception("Strategy processing failed")

        finally:
            strategy_queue.task_done()

        
def dispatch_tick(tick):
    strategy_queue.put(tick)
    database_queue.put(tick)
    logger.debug(f"Queue size | strategy={strategy_queue.qsize()} database={database_queue.qsize()}") 

def main():
    logger.info("paper Trading application start>>>>>>>>>>>>>>>>>>>")

    db_thread = threading.Thread(target=database_worker, daemon=True, name="DatabseWorker")
    db_thread.start()

    strategy_thread = threading.Thread(target=strategy_worker, daemon=True, name="StrategyWorker")
    strategy_thread.start()


    client = Client();client.login()
    logger.info("login succesful")

    sws = client.create_sws()

    def on_open(ws):
        logger.info("websocket connected")

        sws.subscribe(default_correlation_id, default_mode, default_token_list)
        logger.info("Subcription sent")

    def on_data(ws, message):
        try:
            tick = Tick(message)
            dispatch_tick(tick)

        except Exception:
            logger.exception("Error Processing tick")
        

    def on_error(ws, error):
        logger.error(f"Websocket error: {error}")

    def on_close(ws):
        logger.warning("WebSocket connnection closed")
    
    # ---------------- Assign callbacks ---------------- #

    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close


    ws_thread = threading.Thread(target=sws.connect, daemon=True, name="WebsocketWorker")
    ws_thread.start()

    logger.info("Paper Trading System is running")

    try:
        ws_thread.join()
    except KeyboardInterrupt:
        logger.info("Paper Trading Application Stopped")


# ---------------- Start ---------------- #

if __name__ == "__main__":
    main()
    
    
    
    
    