import { Component, OnInit } from '@angular/core';
import { HttpService } from './services/http.service';
import {
  trigger,
  state,
  style,
  animate,
  transition
} from '@angular/animations';
import { MatSnackBar } from '@angular/material';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  animations: [
    trigger('openClose', [
      state('open', style({
      })),
      state('closed', style({
        height: '0px',
      })),
      transition('open => closed', [
        animate('0.5s')
      ]),
      transition('closed => open', [
        animate('0.25s')
      ]),
    ]),
  ]
})
export class AppComponent {
  private initUrl = "simulationInit";
  private undoInitUrl = "simulationInitUndo";
  private startedUrl = "simulationStarted";


  // for angular animations
  private createOpen: boolean = false;
  private showOpen: boolean = false;
  private scheduleOpen: boolean = false;
  private forecastOpen: boolean = false;

  private creationFinished: boolean = false;

  toggleCreate() {
    this.createOpen = !this.createOpen;
    if (this.createOpen) {
      this.showOpen = false;
      this.scheduleOpen = false;
      this.forecastOpen = false;
    }
  }
  toggleShow() {
    this.showOpen = !this.showOpen;
    if (this.showOpen) {
      this.createOpen = false;
      this.scheduleOpen = false;
      this.forecastOpen = false;
    }
  }
  toggleSchedule() {
    this.scheduleOpen = !this.scheduleOpen;
    if (this.scheduleOpen) {
      this.showOpen = false;
      this.createOpen = false;
      this.forecastOpen = false;
    }
  }
  toggleForecast() {
    this.forecastOpen = !this.forecastOpen;
    if (this.forecastOpen) {
      this.showOpen = false;
      this.scheduleOpen = false;
      this.createOpen = false;
    }
  }


  constructor(private http: HttpService, private snackbar: MatSnackBar) {
    this.http.makeGetRequest(this.startedUrl)
      .subscribe((data: any) => {
        // this.snackbar.open('', '', {
        //   duration: 3000
        // });
        this.creationFinished = data.is_started;
      },
        // error handling
        (error) => {

          console.log(error);
          this.snackbar.open('Could not get simulation specific data.', '', {
            duration: 3000
          });

        });

  }

  ngOnInit() {


  }

  initSimulation() {
    this.snackbar.open('Please wait a few seconds.', '', {
      duration: 20000
    });
    this.http.makePostRequest(this.initUrl, {})
      .subscribe((data: any) => {
        console.log("successfull init")
        this.snackbar.open('Simulation initialized', '', {
          duration: 3000
        });

      },
        // error handling
        (error) => {
          if ((error.status == 201)||(error.status ==200)) {
            // successfull request
            console.log("successfull init")
            this.snackbar.open('Simulation initialized', '', {
              duration: 3000
            });
            this.creationFinished = true;
            this.createOpen = false;

          } else {
            console.log(error);
            this.snackbar.open('Could not initialize simulation.', '', {
              duration: 3000
            });

          }

        });

  }

  undoInitSimulation() {
    this.http.makePostRequest(this.undoInitUrl, {})
      .subscribe((data: any) => {
        console.log("successfull undoing")
        this.snackbar.open('Undoing successful', '', {
          duration: 3000
        });
        this.creationFinished = true;
        this.createOpen = false;

      },
        // error handling
        (error) => {
          if ((error.status == 201)||(error.status ==200)) {
            // successfull request
            console.log("undoing successfull")
            this.snackbar.open('Undoing successful', '', {
              duration: 3000
            });
            this.creationFinished = false;

          } else {
            console.log(error);
            this.snackbar.open('Could not undo simulation initialization.', '', {
              duration: 3000
            });

          }

        });
  }

}
