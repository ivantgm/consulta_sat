<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;
require("PHPMailer/PHPMailer.php"); 
require("PHPMailer/SMTP.php"); 
require("PHPMailer/Exception.php");
require_once "const.php";

function send_email($to, $subject, $body) {
    $mail = new PHPMailer(true);
    try {
        $mail->isSMTP(); 
        $mail->CharSet    = "UTF-8";                       
        $mail->Host       = MAIL_HOST; 
        $mail->SMTPAuth   = true;               
        $mail->Username   = MAIL_USER; 
        $mail->Password   = MAIL_PASS;
        $mail->SMTPSecure = 'ssl';
        $mail->Port       = 465;                        
        $mail->setFrom(MAIL_USER, 'Contato Miliogo');
        $mail->addAddress($to);     
        $mail->isHTML(true);                                  
        $mail->Subject = $subject;
        $mail->Body    = $body;
        $mail->AltBody = strip_tags($body);
        $mail->send();
        return true;
    } catch (Exception $e) {
        return false;
    }
}