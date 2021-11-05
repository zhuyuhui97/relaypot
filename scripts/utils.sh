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
    if [ ! -z $2 ]; then
            CFG_PARAM="-c $2"
    fi
    if [ $1 = 'backend' ]; then
        
        PYTHONPATH=$RELAYPOT_HOME/src twistd --pidfile=$RUN_DIR/backend.pid --logfile=$LOG_DIR/backend.log $BKMOD $CFG_PARAM
    else 
        PYTHONPATH=$RELAYPOT_HOME/src twistd --pidfile=$RUN_DIR/$1.pid --logfile=$LOG_DIR/$1.log $FRMOD -p $1 $CFG_PARAM
    fi
}


stop(){
    kill `cat $RUN_DIR/$1.pid`
}

watch(){
    tail -f $LOG_DIR/$1.log
}

$*