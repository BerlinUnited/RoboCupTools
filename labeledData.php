<?php
  include 'php/listcontents.php';
  
  $result = "{\n";
  foreach ($games as $key => $g) {
    
    if(sizeof($g->logs) > 0) {
      
      $game_data = array();
      foreach ($g->logs as $key => $log) {
        
        $log_data = array();
        
        foreach ($log->json as $jname => $jpath) {
          if($jname != 'blank') {
            //$result .= $jname.": ";
            //echo $jname . " - " . $jpath . "<br>";
            //$result .= $jpath;
            //$result .= file_get_contents($jpath);
            //$result .= "\n";
            
            array_push ($log_data, "\"".$jname."\": ".file_get_contents($jpath));
          }
        }
        
        if(sizeof($log_data) > 0) {
          array_push($game_data, "{".join(",\n",$log_data)."}");
        }
      }
      
      if(sizeof($game_data) > 0) {
        $name = $g->name.'-'.$g->half;
        $result .= "\"".$name."\": [\n";
        $result .= join(",\n",$game_data);
        $result .= "]\n";
      }
    }
  }
  $result .= "}";

  echo $result;
?>