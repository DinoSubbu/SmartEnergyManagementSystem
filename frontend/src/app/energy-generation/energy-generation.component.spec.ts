import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EnergyGenerationComponent } from './energy-generation.component';

describe('EnergyGenerationComponent', () => {
  let component: EnergyGenerationComponent;
  let fixture: ComponentFixture<EnergyGenerationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EnergyGenerationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EnergyGenerationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
