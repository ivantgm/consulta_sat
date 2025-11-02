<?php
{
  require "const.php";
  
  $conn = mysqli_connect(MY_HOST, MY_USER, MY_PASS);
  mysqli_select_db($conn, MY_DB);

  $sql = "select now() as n";
  $result = mysqli_query($conn, $sql);
  $obj = mysqli_fetch_object($result);
  $server_time = $obj->n;
  mysqli_free_result($result);

  function write_log($msg){
    $fp = fopen("log.txt", "a");    
    $escreve = fwrite($fp, $msg . "\n");        
    fclose($fp);
  }  
}

?>