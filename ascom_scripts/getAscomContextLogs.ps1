
$LocalLogPath = "\\server\shared\Ascom\Logs\"
$computers = @( 'computername1', 'computername2')

$AscomLogPath = '\c$\Users\username\Appdata\Local\Ascom\Logs'
foreach($computer in $computers){
    $destPath = $LocalLogPath + $computer
    # Write-Host $destPath, (test-path $destPath)
    if (!(test-path $destPath)){
        # Write-Host "Does not exist: " + $destPath
        New-Item -ItemType Directory -Force -Path $destPath > $null
    }
    # Write-Host "SRC Path: ", (join-path ('\\' + $computer) $AscomLogPath), (test-path $destPath)
    $srcPath = (join-path ('\\' + $computer) $AscomLogPath)
    get-ChildItem $srcPath  | foreach {
        # Write-host "Test Dest: ", (test-path $destPath)
        if (test-path $destPath){
            # write-host "Destination: ", $destPath
            # Write-Host ( $srcPath + "\" + $_.Name)
            $tFile = $srcPath + "\" + $_.Name
            if (test-path $tFile){
                # Write-Host "Test Path True"
                Copy-Item -Path $tFile -Destination ($destPath + "\" + $computer +"_" + $_.LastWriteTime.ToString("yyyyMMddHHmm") + "_" +$_.Name)
                Write-Host ($computer +"_" + $_.LastWriteTime.ToString("yyyyMMddHHmm") + "_" +$_.Name)
            }
            else {
                # Write-Host "Test path False"
            }
        }
    }
}