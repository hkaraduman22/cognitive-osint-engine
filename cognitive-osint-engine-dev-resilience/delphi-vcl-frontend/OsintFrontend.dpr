program OsintFrontend;

uses
  Vcl.Forms,
  MainForm in 'MainForm.pas' {FrmMain},
  LoginForm in 'Forms\LoginForm.pas' {FrmLogin},
  RegisterForm in 'Forms\RegisterForm.pas' {FrmRegister},
  SearchForm in 'Forms\SearchForm.pas' {FrmSearch},
  ResultsForm in 'Forms\ResultsForm.pas' {FrmResults},
  HistoryForm in 'Forms\HistoryForm.pas' {FrmHistory},
  AdminForm in 'Forms\AdminForm.pas' {FrmAdmin},
  UApiConfig in 'Api\UApiConfig.pas',
  UHttpApiClient in 'Api\UHttpApiClient.pas',
  UJwtTokenStore in 'Utils\UJwtTokenStore.pas',
  UAuthService in 'Services\UAuthService.pas',
  USearchService in 'Services\USearchService.pas',
  UResultsService in 'Services\UResultsService.pas',
  UHistoryService in 'Services\UHistoryService.pas',
  UAdminService in 'Services\UAdminService.pas';

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.CreateForm(TFrmLogin, FrmLogin);
  Application.Run;
end.
