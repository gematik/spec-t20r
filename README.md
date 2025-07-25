# Telematikinfrastruktur

![gematik](/images/gematik-logo.svg)

Hier sind die Festlegungen zur Telematikinfrastruktur dokumentiert. Es werden insbesondere die Komponenten der anwendungsübergreifenden Telematikinfrastruktur sowie deren Schnittstellen beschrieben.

## Inhalt

- [Telematikinfrastruktur](#telematikinfrastruktur)
  - [Inhalt](#inhalt)
  - [ZETA](#zeta)
  - [Branch Modell](#branch-modell)
  - [Lizenzbedingungen](#lizenzbedingungen)

## ZETA

Der Zugang zu Diensten der Telematikinfrastruktur 2.0 erfolgt über das Internet. Zero Trust Access (ZETA) ist eine Lösung, die die Sicherheit und den Zugriff auf diese Dienste gewährleistet. Es basiert auf dem Prinzip, dass keinem Client oder Benutzer automatisch vertraut wird, sondern jeder Zugriff überprüft und autorisiert werden muss.

[ZETA API](https://github.com/gematik/zeta/docs/zeta-api.md)

## Branch Modell

In diesem Repository werden Branches verwendet, um den Status der Weiterentwicklung und das Review von Änderungen abzubilden.

Folgende Branches werden verwendet

- *main* (enthält den letzten freigegebenen Stand der Entwicklung; besteht permanent)
- *develop* (enthält den Stand der fertig entwickelten Features und wird zum Review durch Industriepartner und Gesellschafter verwendet; basiert auf main; nach Freigabe erfolgt ein merge in main und ein Release wird erzeugt; besteht permanent)
- *feature/<name>* (in feature branches werden neue Features entwickelt; basiert auf develop; nach Fertigstellung erfolgt ein merge in develop; wird nach dem merge gelöscht)
- *hotfix/<name>* (in hotfix branches werden Hotfixes entwickelt; basiert auf main; nach Fertigstellung erfolgt ein merge in develop und in main; wird nach dem merge gelöscht)
- *concept/<name>* (in concept branches werden neue Konzepte entwickelt; basiert auf develop; dient der Abstimmung mit Dritten; es erfolgt kein merge; wird nach Bedarf gelöscht)
- *misc/<name>* (nur für internen Gebrauch der gematik; es erfolgt kein merge; wird nach Bedarf gelöscht)

## Lizenzbedingungen

Copyright (c) 2022 gematik GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
