RELAYPOT_HOME='/home/pot/relaypot'
FRMOD='relaypot'
BKMOD='relaypot-backend'
RUN_DIR='/var/run/relaypot'
LOG_DIR='/var/log/relaypot'

mkdir -p $RUN_DIR

. $RELAYPOT_HOME/scripts/config

init_dirs(){
    if [ ! -d $RUN_DIR ]; then
        sudo mkdir -p $RUN_DIR
        sudo chown pot:pot $RUN_DIR
    fi

    if [ ! -d $LOG_DIR ]; then
        sudo mkdir -p $LOG_DIR
        sudo chown pot:pot $LOG_DIR
    fi
}

start(){
    if [ $1 = 'backend' ]; then
        PYTHONPATH=$RELAYPOT_HOME/src twistd --pidfile=$RUN_DIR/backend.pid --logfile=$LOG_DIR/backend.log $BKMOD -p 6668
    else 
        PYTHONPATH=$RELAYPOT_HOME/src twistd --pidfile=$RUN_DIR/$1.pid --logfile=$LOG_DIR/$1.log $FRMOD -p $1 -b $BACKEND
    fi
}


stop(){
    kill `cat $RUN_DIR/$1.pid`
}

watch_log(){
    tail -f $LOG_DIR/$1.log
}

$*