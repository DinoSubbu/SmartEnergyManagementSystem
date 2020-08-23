import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CurrentGenerationComponent } from './current-generation.component';

describe('CurrentGenerationComponent', () => {
  let component: CurrentGenerationComponent;
  let fixture: ComponentFixture<CurrentGenerationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CurrentGenerationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CurrentGenerationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
