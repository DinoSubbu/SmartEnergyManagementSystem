import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GasBoilerComponent } from './gas-boiler.component';

describe('GasBoilerComponent', () => {
  let component: GasBoilerComponent;
  let fixture: ComponentFixture<GasBoilerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GasBoilerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GasBoilerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
