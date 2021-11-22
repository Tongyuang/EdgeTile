from core.logging.edge_logging import EdgeLogger

if __name__ == "__main__":
    edge_logger = EdgeLogger("uav0000137_00458_v", "tile3x3_ultrafast")
    edge_logger.collect_logs()
    # edge_logger.load_client_or_server_log("data/exps/ILSVRC2015_val_00000000_tile3x3_2019_11_30/client.log")
    edge_logger.parse_logs()