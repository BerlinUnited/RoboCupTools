<?php
  include 'php/listcontents.php';
  
  
  $data = array();
  
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
        array_push($data, "\"".$name."\": [\n".join(",\n",$game_data)."]\n");
      }
    }
  }
  
  echo "{\n".join(",\n",$data)."}";
?>