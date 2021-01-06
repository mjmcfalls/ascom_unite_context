# ascomComplianceReport

##### Build and push docker image:
```docker build -t msj/ascomreport:1 . ; docker save msj/ascomreport:1 -o c:\dev\images\msj_ascomreport_1.tar;  winscp /command "open scp://inno-gitlab.msj.org/" "put c:\dev\images\msj_ascomreport_1.tar /home/tecmmx/" "exit"```

tDevices:
FirmwareVersion
SerialNumber
IPAddress

Apps:

com.ascom.medicview/apps-list/apps.app_name	Setup	9789406192110951353
com.ascom.medicview/apps-list/apps.app_name	Phone	9064338438475630123
com.ascom.medicview/apps-list/apps.app_name	Clock	801385939761217464
com.ascom.medicview/apps-list/apps.app_name	PTT	7564195215672340879
com.ascom.medicview/apps-list/apps.app_name	Browser	7255832417732727760
com.ascom.medicview/apps-list/apps.app_name	Personal security	642520829192444339
com.ascom.medicview/apps-list/apps.app_name	Settings	6298294726772882576
com.ascom.medicview/apps-list/apps.app_name	My Services	5723203182465076767
com.ascom.medicview/apps-list/apps.app_name	Search	5710978759458982735
com.ascom.medicview/apps-list/apps.app_name	Music	4870472282655128632
com.ascom.medicview/apps-list/apps.app_name	Calculator	4564190426170815308
com.ascom.medicview/apps-list/apps.app_name	Unite Context	2574888104202849261
com.ascom.medicview/apps-list/apps.app_name	Gallery	17845401502286784743
com.ascom.medicview/apps-list/apps.app_name	Calendar	17612716204027717987
com.ascom.medicview/apps-list/apps.app_name	Settings	17479598783108620629
com.ascom.medicview/apps-list/apps.app_name	Voice Dialer	17479563495707360577
com.ascom.medicview/apps-list/apps.app_name	Email	17042426002025490876
com.ascom.medicview/apps-list/apps.app_name	Myco Launcher	15007109137499193373
com.ascom.medicview/apps-list/apps.app_name	Camera	14119271812612341795
com.ascom.medicview/apps-list/apps.app_name	Contacts	12804620013844685252
com.ascom.medicview/apps-list/apps.app_name	Sound Recorder	10836854091630595316
com.ascom.medicview/apps-list/apps.app_name	Downloads	10394030973875740092


```Select CurrentCallNo, tDevices.Description, tPortables.UnitId, tDevices.FirmwareVersion, SerialNumber, IPAddress,  LoginTime, Key, Value, ListIndex, tPortables.DeviceType FROM tDevices INNER JOIN tPortables ON tPortables.UnitID = tDevices.UnitID INNER JOIN tListParameters ON tListParameters.PortableId = tPortables.Id```


Get devices and associated hardware info:
```
SELECT t.Id, t.CallNo, d.DeviceType, t.UnitID, t.Description, t.LoginTime, d.FirmwareVersion, d.SerialNumber, d.IPAddress
FROM tPortables t
INNER JOIN tDevices d on t.UnitID = d.UnitID
```
