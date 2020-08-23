import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpService } from '../services/http.service';
import { MatSnackBar } from '@angular/material';
import { formatDate } from '@angular/common';
import { MatTableDataSource } from '@angular/material/table';
import { CommonModule } from '@angular/common';  


@Component({
  selector: 'app-gas-boiler',
  templateUrl: './gas-boiler.component.html',
  styleUrls: ['./gas-boiler.component.scss']
})


export class GasBoilerComponent implements OnInit {

  private buildings = [];
  private latitude : number = null;
  private longitude : number = null;
  private latlongFlag : boolean = false;
  private gasBoilerDataFlag : boolean = false;
  private gasBoilerDataSource;
  private timestampRegexToReplace : RegExp = /[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}/;
  private timestampRegex : RegExp = /[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:[0-9]{2}:[0-9]{2})/;



  displayedColumns: string[][] = [
    ["timestamp", "hotWaterPower", "spaceHeatingPower", "powerOutputBoiler", "fuelInputBoiler"]
  ];

  dataSource: any[] = [];

  constructor(private http: HttpService, private snackbar: MatSnackBar) 
  {
    let requestBuildings = this.http.makeGetRequest("getBuildings");
    
    requestBuildings.subscribe(
      (buildingData: any) => {
        //console.log(buildingData)
        // connection successfull, but empty array returned
        if(buildingData.length == 0) {
          snackbar.open('Building data is not available in database yet.', '', {
            duration: 2000
          });
          return;
        }

        snackbar.open('Latest Building data gathered.', '', {
          duration: 2000
        });
        this.buildings = buildingData;
      },
      // error handling
      error => {
        console.log(error);
        snackbar.open('Could not get building data.', '', {
          duration: 3000
        });

      });

  }

  ngOnInit() {
  }

  changeBuilding(buildingName : string) {
    for (var i=0; i < this.buildings.length; i++) {
      if(this.buildings[i]['name'] == buildingName){
        this.latlongFlag = true;
        this.latitude = this.buildings[i]['lat']
        this.longitude = this.buildings[i]['long']
      }
    }

    let requestGasBoiler = this.http.makeGetRequestAddOption("gasBoilerLatest", buildingName);
    requestGasBoiler.subscribe(
      (gasBoilerData: any) => {
        console.log(gasBoilerData)
        // connection successfull, but empty array returned
        if(gasBoilerData.length == 0) {
          this.snackbar.open('Gas Boiler data is not available in database yet.', '', {
            duration: 2000
          });
          return;
        }

        this.snackbar.open('Latest Gas Boiler data gathered.', '', {
          duration: 2000
        });
        
        for (var i=0; i < gasBoilerData.length; i++) {
          let match = gasBoilerData[i]['timestamp'].match(this.timestampRegex);
          gasBoilerData[i]['timestamp'] = gasBoilerData[i]['timestamp'].replace(this.timestampRegexToReplace, match[1]);
          }
          

        this.gasBoilerDataFlag = true;
        this.gasBoilerDataSource = new MatTableDataSource(gasBoilerData);

      },
      // error handling
      error => {
        console.log(error);
        this.snackbar.open('Could not get Gas Boiler data.', '', {
          duration: 3000
        });

      });

  }

}
