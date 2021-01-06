[CmdletBinding(
    SupportsShouldProcess = $True
)]
param(
    [String]$File,
    [string]$units,
    [string]$xcp

)
Function Remove-Duplicates {
    [CmdletBinding(
        SupportsShouldProcess = $True
    )]
    Param(
        [array]$File
    )
    # $File | Select-Object -Unique | Where-Object {}
    # Remove Duplicates
    # $tempArray = $File.Clone()
    for($i=0; $i -lt ($File.length); $i++){
        for($j=0; $j -lt ($File.length); $j++){
            # Write-Host $File[$i].staticPhoneNumber
            if(($File[$i]) -and ($File[$j])){
                if($File[$i].staticPhoneNumber -eq $File[$j].staticPhoneNumber){
                    if ($i -ne $j){
                        # Write-Host "Found duplicate: $($File[$i].staticPhoneNumber), $($File[$j].staticPhoneNumber)"
                        if($File[$i].lastStatusUpdateTime -ge $File[$j].lastStatusUpdateTime){
                            # Write-Host "$($i) - $($File[$i].lastStatusUpdateTime) >= $($j) - $($File[$j].lastStatusUpdateTime)"
                            $File[$i] = $Null
                        }
                        elseif($File[$i].lastStatusUpdateTime -lt $File[$j].lastStatusUpdateTime){
                            # Write-Host "$($i) - $($File[$i].lastStatusUpdateTime) < $($j) - $($File[$j].lastStatusUpdateTime)"
                            $File[$j] = $Null
                        }
                    }
                }
            }
        }
    }
    $File
}

Function Merge-Results {
    [CmdletBinding(
        SupportsShouldProcess = $True
    )]
    Param(
        [array]$Results,
        [object]$Phones
    )
    # Write-Host "Merge DbResults"
    for($i=0; $i -lt ($Phones.length); $i++){
        for($j=0; $j -lt ($Results.length); $j++){
            if($Phones[$i].PhoneNumber -eq $Results[$j].staticPhoneNumber){
                # Write-Host "$($Phones[$i].PhoneNumber) matches $($Results[$j].staticPhoneNumber)"
                # Write-Host "User: $($Results[$j].lastLoginName)"
                if($Results[$j].lastLoginName){
                    $user = Get-Aduser ($Results[$j].lastLoginName)
                    $Phones[$i].givenName = $user.GivenName
                    $Phones[$i].surname = $user.Surname
                }
                $Phones[$i].lastLoginName = $Results[$j].lastLoginName
                $Phones[$i].lastLoginTime = $Results[$j].lastLoginTime
                $Phones[$i].lastStatusUpdateTime = $Results[$j].lastStatusUpdateTime
                $Phones[$i].phoneId = $Results[$j].phoneId
                break;
            }
        }
    }
    $Phones
}
Function Get-Hospital{
    Param(
        $phoneNumber,
        $phones
    )
    Foreach($item in $phones){
        if ($item.PhoneNumber -eq $phoneNumber){
            $temp = @{
                'unit'= $item.Unit
                'hospital'=$item.Hospital}
            $temp
            break
        }
    }

}

Function Process-XCP {
    [CmdletBinding(
        SupportsShouldProcess = $True
    )]
    Param(
        [Parameter(Mandatory = $True)]
        [string]
        $File
    )
    $psobjs = [System.Collections.ArrayList]@()
    $psobjSrc = [PSCustomObject]@{
        phoneNumber = ''
        givenName = ''
        surname = ''
        lastLoginName = ''
        lastLoginTime = ''
        lastStatusUpdateTime = ''
        phoneId = ''
        appVersion = ''
    }
    for ($i = 0; $i -lt $xml.dmExport.device.length; $i++) {
        $psobj = $psobjSrc.psobject.Copy()
        # $psobj
        if ($i -eq $xml.dmExport.device.length - 1) {
            # Write-Host "'$($xml.dmExport.device[$i].id)'"
            # $oString += "'$($xml.dmExport.device[$i].id)'"
            $psobj.phoneNumber = $xml.dmExport.device[$i].id
            $psobjs.add($psobj)  | Out-Null
        }
        else {
            # Write-Host "'$($xml.dmExport.device[$i].id)'"
            # $oString += "'$($xml.dmExport.device[$i].id)',"
            $psobj.phoneNumber = $xml.dmExport.device[$i].id
            $psobjs.add($psobj) | Out-Null
        }
    }
    $psobjs
}

Function Get-OfflineState {
    [CmdletBinding(
        SupportsShouldProcess = $True
    )]
    Param(
        [Parameter(Mandatory = $True)]
        $Phonenumber,
        $xcp
    )
    # Write-Host "$($xcp)"
   foreach($item in $xcp){
    #    Write-Host "item - $($item)"
       if ($item.PhoneNumber -eq $PhoneNumber){
        # Write-Host "$($item.PhoneNumber) - $($Phonenumber)"
           $True
           break
       }
   }
}

Function Add-MissingFromXcp {
    param(
        $xcp,
        $data
    )
    # Foreach($item in $xcp){
    #     $exists = $False
    #     # Write-Host "Checking $($item.PhoneNumber)"
    #     Foreach($d in $data){
    #         # Write-Host "$($d.staticPhoneNumber)- $($item.PhoneNumber)"
    #         if ($d.staticPhoneNumber -eq $item.PhoneNumber){
    #             $exists  = $True
    #             break
    #         }
    #     }
    #     if($exists -eq $False){
            $psobjSrc = [PSCustomObject]@{
                phoneId = ''
                staticPhoneNumber = ''
                lastLoginName = ''
                lastLoginTime = ''
                lastStatusUpdateTime = ''
                appVersion = ''
                hospital = ''
                unit = ''
                offline = ''
                }
      
    #         # Write-Host "Adding: $($item.PhoneNumber)"
            $psObjSrc.staticPhoneNumber = $item.PhoneNumber
            $data += $psObjSrc  
    #         }
    #     else{ 
    #         # Write-Host "Skipping: $($item.PhoneNumber)"
    #     }
        $data
    # }
}


$psobjs = @()
$psobjSrc = [PSCustomObject]@{
    phoneId = ''
    staticPhoneNumber = ''
    lastLoginName = ''
    lastLoginTime = ''
    lastStatusUpdateTime = ''
    appVersion = ''
    hospital = ''
    unit = ''
    offline = ''
}

# [xml]$xml = Get-Content $File
$cData = Import-Csv -Path $File
$phones = Import-Csv -Path $units
[xml]$xml = Get-Content $xcp
$xFiles = Process-XCP -File $xml

# $xFiles
# $filteredData = Add-MissingFromXcp -xcp $xFiles -data $cData 
$filteredData = Remove-Duplicates -File $cData


# Write-Host "Building output obj"/
# $filteredData.length
foreach($item in $filteredData){
    # $item.getType()
    if($item.staticPhoneNumber){
        # Write-Host "Processing $($item.staticPhoneNumber)"
        $offline = $False
        $offline = Get-OfflineState -Phonenumber $item.staticPhoneNumber -xcp $xFiles

        $hospital = Get-Hospital -Phones $phones -phonenumber $item.staticPhoneNumber
        
        $psObjCopy = $psobjSrc.psobject.Copy()

        $psObjCopy.phoneId = $item.phoneId
        $psObjCopy.staticPhoneNumber = $item.staticPhoneNumber
        $psObjCopy.lastLoginName = $item.lastLoginName
        $psObjCopy.lastLoginTime = $item.lastLoginTime
        $psObjCopy.lastStatusUpdateTime = $item.lastStatusUpdateTime
        $psObjCopy.phoneId = $item.phoneId
        $psObjCopy.appVersion = $item.appVersion
        $psObjCopy.hospital = $hospital.hospital
        $psObjCopy.unit = $hospital.unit
        $psObjCopy.offline = $offline
        
        $psobjs += $psObjCopy
    }
}

$psobjs 



