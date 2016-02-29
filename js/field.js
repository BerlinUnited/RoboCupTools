function drawField(ctx, width, height)
{
  var xOwnGround = 9000;
  var xOppGround = 700;
  var yRightBorder = 6000;
  var yLeftBorder = 700;

  var goalPostRadius = 50;
  var borderStripWidth = 700;
  var lineWidth = 50;
  
  ctx.beginPath();
  ctx.rect(0,0,7400,10400);
  ctx.fillStyle = '#00AA00';
  ctx.fill();
  //Field Borders      
  ctx.rect(yLeftBorder,xOppGround,yRightBorder,xOwnGround)
  ctx.lineWidth = lineWidth;
  ctx.strokeStyle = 'white';
  ctx.stroke();

  //Center Line
  ctx.beginPath();
  ctx.moveTo(yLeftBorder, height/2);
  ctx.lineTo(7400-borderStripWidth, height/2);
  ctx.stroke();
  //Opp Penalty  Mark
  ctx.translate((width/2),(height/2));
  ctx.beginPath();
  ctx.arc(0, -1300, 50, 0, 2 * Math.PI, false);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.stroke();
  //Own Penalty  Mark
  ctx.beginPath();
  ctx.arc(0, 1300, 50, 0, 2 * Math.PI, false);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.stroke();
  //Circle
  ctx.beginPath();
  ctx.arc(0, 0, borderStripWidth, 0, 2 * Math.PI, false);
  ctx.stroke();
  //Own Goal Posts
  ctx.beginPath();
  ctx.arc(750, 4500, goalPostRadius, 0, 2 * Math.PI, false);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(-750, 4500, goalPostRadius, 0, 2 * Math.PI, false);
  ctx.stroke();
  
  //Own Goal
  ctx.fillStyle = '#99AAFF';
  ctx.fillRect(-750, 4500, 1500, 500);
  
  ctx.beginPath();
  ctx.moveTo(750, 4500);
  ctx.lineTo(750, 4500+500);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-750, 4500);
  ctx.lineTo(-750, 4500+500);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-750, 4500+500);
  ctx.lineTo(750, 4500+500);
  ctx.stroke();
  //Opp Goal Posts
  ctx.beginPath();
  ctx.arc(750, -4500, goalPostRadius, 0, 2 * Math.PI, false);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(-750, -4500, goalPostRadius, 0, 2 * Math.PI, false);
  ctx.stroke();
  
  //Opp Goal
  ctx.fillStyle = '#FFAA99';
  ctx.fillRect(-750, -4500, 1500, -500);
  
  ctx.beginPath();
  ctx.moveTo(750, -4500);
  ctx.lineTo(750, -4500-500);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-750, -4500);
  ctx.lineTo(-750, -4500-500);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-750, -4500-500);
  ctx.lineTo(750, -4500-500);
  ctx.stroke();

  //Own Penalty Area
  ctx.beginPath();
  ctx.moveTo(1100, 4500);
  ctx.lineTo(1100, 4500-500);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-1100, 4500);
  ctx.lineTo(-1100, 4500-500);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-1100, 4500-500);
  ctx.lineTo(1100, 4500-500);
  ctx.stroke();

  //Opp Penalty Area
  ctx.beginPath();
  ctx.moveTo(1100, -4500);
  ctx.lineTo(1100, -4500+500);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-1100, -4500);
  ctx.lineTo(-1100, -4500+500);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-1100, -4500+500);
  ctx.lineTo(1100, -4500+500);
  ctx.stroke();

  ctx.translate(-(width/2),-(height/2));
}

function drawRobot(ctx, width, height,x,y,rot)
{
  var image = document.getElementById("nao");
  
  //Draw Robot: Image-length: 557, Image-height = 865
  ctx.translate(x, y);
  ctx.rotate(rot);
  
  var scale = 0.7;
  ctx.scale(scale, scale);
  ctx.translate(-279, -433);
  ctx.drawImage(image, 0, 0);
  ctx.translate(279, 433);
  ctx.scale(1.0/scale, 1.0/scale);
  
  ctx.rotate(-rot);
  ctx.translate(-x, -y);
}

function drawBall(ctx, width, height,x,y) 
{
  ctx.translate(x, y);
  ctx.beginPath();
  ctx.arc(0, 0, 70, 0, 2 * Math.PI, false);
  ctx.fillStyle = '#FFAA99';
  ctx.fill();
  ctx.translate(-x, -y);
}

function draw(x,y,rot, bx, by)
{
  var canvas = document.getElementById('canvas');
  if (canvas.getContext)
  {
    var width = canvas.width;
    var height = canvas.height;

    

    //var image = document.getElementById("nao");

    var ctx = canvas.getContext('2d');
    //ctx.restore();
    //ctx.save();
    if(typeof InstallTrigger !== 'undefined'){
      //HACK: Scales the canvas if browser is firefox
      ctx.scale(0.7,0.7);
    } 
    
      drawField(ctx, width, height);
      
      // global field transform
      
      ctx.translate((width/2),(height/2));
      ctx.rotate(-Math.PI/2.0);
      ctx.scale(1, -1);
  
      drawRobot(ctx, width, height, x,y,rot);
      drawBall(ctx, width, height, bx,by);
      
      ctx.scale(1, -1);
      ctx.rotate(Math.PI/2.0);
      ctx.translate(-(width/2),-(height/2));
  }//end if  
}//end draw