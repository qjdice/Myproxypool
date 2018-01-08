<?php 
$config = include('config.php');

class Proxy{

    protected $db_host = null;
    protected $db_password = null;
    protected $db_port = null;
    static protected $connect = null;
    public function __construct($attrubes){
        extract($attrubes);
        $this->db_host = $DB_HOST;
        $this->db_password = $DB_PASSWORD;
        $this->db_port = $DB_PORT;
        if(!self::$connect){
            self::$connect = new Redis();
            self::$connect->connect('127.0.0.1', 6379);
            if($this->db_password){
                self::$connect->auth($this->db_password);
            }
        }

    }

    public function get(){
        $res = self::$connect->rpop("proxies");
        if($res){
            die($res);
        }else{
            die('Inval proxies');
        }
    }

    public function len(){

        $res = self::$connect->llen('proxies');
        exit((string) $res);
    }
}


$m = $_GET['m'] ?? null;

$proxy = new proxy($config);
if(!$m || !method_exists($proxy,$m)){
    exit('Hello Word');
}
$proxy->$m();
