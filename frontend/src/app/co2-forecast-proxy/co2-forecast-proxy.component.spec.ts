import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { Co2ForecastProxyComponent } from './co2-forecast-proxy.component';

describe('Co2ForecastProxyComponent', () => {
  let component: Co2ForecastProxyComponent;
  let fixture: ComponentFixture<Co2ForecastProxyComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ Co2ForecastProxyComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(Co2ForecastProxyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
