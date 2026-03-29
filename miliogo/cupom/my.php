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
    file_put_contents("miliogo_log.txt", date("Y-m-d H:i:s") . " - " . $msg . "\n", FILE_APPEND);
  }  
}
?>