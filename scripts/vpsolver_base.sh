#!/usr/bin/false

init_vars() {
    CMD="$0 $*"
    BIN_DIR=$BASEDIR/../bin/
    PATH=$BIN_DIR:$PATH
    TMP_DIR=`mktemp -d -t XXXXXXXXXX`
    trap "rm -rf $TMP_DIR;" SIGHUP SIGINT SIGTERM EXIT
    instance_file=""
    model_file=""
    afg_file=""
    sol_file=""
    vbpsol_opts=""
    options=""
}

usage(){
    echo -e "Usage:"
    echo -e "  $0 --vbp/--mvp instance.vbp/.mvp"
    echo -e "  $0 --afg graph.afg"
    echo -e "  $0 --mps/--lp model.mps/.lp"
    echo -e "  $0 --mps/--lp model.mps/.lp --afg graph.afg"
}

error(){
    echo "Command line: "$CMD
    echo "Error: invalid arguments."
    usage
    exit 1
}

parse_args(){
    while true;
    do
    case "$1" in
        --mps)
            if [[ -z "$model_file" && -n "$2" && -e "$2" && "$2" =~ \.mps$ ]]; then
                model_file=$2
            else
                error
            fi
            shift 2;;

        --lp)
            if [[ -z "$model_file" && -n "$2" && -e "$2" && "$2" =~ \.lp$ ]]; then
                model_file=$2
            else
                error
            fi
            shift 2;;

        --afg)
            if [[ -z "$afg_file" && -n "$2" && -e "$2" && "$2" =~ \.afg$ ]]; then
                afg_file=$2
            else
                error
            fi
            shift 2;;

        --vbp)
            if [[ -z "$instance_file" && -n "$2" && -e "$2" && "$2" =~ \.vbp$ ]]; then
                instance_file=$2
            else
                error
            fi
            shift 2;;

        --mvp)
            if [[ -z "$instance_file" && -n "$2" && -e "$2" && "$2" =~ \.mvp$ ]]; then
                instance_file=$2
            else
                error
            fi
            shift 2;;

        --wsol)
            if [[ -z "$sol_file" && -n "$2" ]]; then
                sol_file=$2
            else
                error
            fi
            shift 2;;

        --pyout)
            if [[ -z "$vbpsol_opts" ]]; then
                vbpsol_opts="0 1"
            else
                error
            fi
            shift 1;;

        --options)
            if [[ -n "$2" ]]; then
                options=$2
            else
                error
            fi
            shift 2;;

        *)
            if [[ -n "$1" ]]; then
                error
            else
                break
            fi
    esac
    done
}

generate_model(){
    if [[ -z "$instance_file" && -z "$model_file" && -z "$afg_file" ]]; then
        error
    fi

    if [[ -n "$instance_file" ]]; then
        if [[ -n "$afg_file" || -n "$model_file" ]]; then
            error
        fi

        afg_file=$TMP_DIR/graph.afg
        model_file=$TMP_DIR/model.mps

        echo -e "\n>>> vbp2afg..."
        vbp2afg $instance_file $afg_file &
        pid=$!
        trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
        wait $pid

        echo -e "\n>>> afg2mps..."
        afg2mps $afg_file $model_file
    elif [[ -n "$afg_file" ]]; then
        if [[ -n "$instance_file" ]]; then
            error
        fi

        if [[ -z $model_file ]]; then
        model_file=$TMP_DIR/model.mps

        echo -e "\n>>> afg2mps..."
        afg2mps $afg_file $model_file
        fi
    fi
}

extract_solution() {
    if [[ -n "$afg_file" && -z "$sol_file" ]]; then
        echo -e "\n>>> vbpsol..."
        vbpsol $afg_file $TMP_DIR/vars.sol $vbpsol_opts
    fi

    if [[ -n "$sol_file" ]]; then
        cp $TMP_DIR/vars.sol $sol_file
    fi
}