[CmdletBinding(
    SupportsShouldProcess = $True
)]
param(
    [String]$File,
    [String]$Csv = "Export.csv",
    [String]$Computer
)


[xml]$xml = Get-Content $File

$objArray = @()

for ($i = 0; $i -lt $xml.dmExport.device.length; $i++) {
    $obj = New-Object -TypeName psobject
    $obj | Add-Member -MemberType NoteProperty -Name PhoneNumber -Value ($xml.dmExport.device[$i].id)
    $objArray += $obj
}

