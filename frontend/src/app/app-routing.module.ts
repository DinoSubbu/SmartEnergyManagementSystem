import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { DayAheadPricesComponent } from './day-ahead-prices/day-ahead-prices.component';
import { BatteryComponent } from './battery/battery.component';
import { GasBoilerComponent } from './gas-boiler/gas-boiler.component';
import { EnergyGenerationComponent } from './energy-generation/energy-generation.component';
import { Co2ForecastProxyComponent } from './co2-forecast-proxy/co2-forecast-proxy.component';
import { ScheduleComponent } from './schedule/schedule.component';
import { AddGeneralComponent } from './add-general/add-general.component';
import { AddWindTurbineComponent } from './add-wind-turbine/add-wind-turbine.component';
import { AddSolarComponent } from './add-solar/add-solar.component';
import { AddBuildingComponent } from './add-building/add-building.component';
import { AddBatteryComponent } from './add-battery/add-battery.component';
import { ComponentsComponent } from './components/components.component';
import { SettingsComponent } from './settings/settings.component';
import { BatteryForecastComponent } from './battery-forecast/battery-forecast.component';
import { CurrentGenerationComponent } from './current-generation/current-generation.component';
import { DemandComponent } from './demand/demand.component';
import { CurrentComponent } from './current/current.component';
import { ScheduleVariationComponent } from './schedule-variation/schedule-variation.component';

const routes: Routes = [
  { path: 'entities', component: HomeComponent },
  { path: 'addWindTurbine', component: AddWindTurbineComponent },
  { path: 'addSolar', component: AddSolarComponent },
  { path: 'addBuilding', component: AddBuildingComponent },
  { path: 'addBattery', component: AddBatteryComponent },
  { path: 'dayAheadPrices', component: DayAheadPricesComponent },
  { path: 'batteryState', component: BatteryComponent },
  { path: 'gasBoilerState', component: GasBoilerComponent },
  { path: 'energyGeneration', component: EnergyGenerationComponent },
  { path: 'co2ForecastProxy', component: Co2ForecastProxyComponent },
  { path: 'currentGeneration', component: CurrentGenerationComponent },
  { path: 'componentsSchedule', component: ComponentsComponent },
  { path: 'schedule', component: ScheduleComponent },
  { path: 'settings', component: SettingsComponent },
  { path: 'scheduleDeviation', component: ScheduleVariationComponent },
  { path: 'batterySchedule', component: BatteryForecastComponent },
  { path: 'demand', component: DemandComponent },
  { path: 'currentOverview', component: CurrentComponent },

  { path: '', redirectTo: '/entities', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
