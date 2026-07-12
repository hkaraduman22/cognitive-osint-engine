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
  USecureStorage in 'Utils\USecureStorage.pas',
  UAuthService in 'Services\UAuthService.pas',
  USearchService in 'Services\USearchService.pas',
  UResultsService in 'Services\UResultsService.pas',
  UHistoryService in 'Services\UHistoryService.pas',
  UAdminService in 'Services\UAdminService.pas';

{$R *.res}

function TryRestorePersistedSession: Boolean;
var
  LAuthService: TAuthService;
  LAuthResult: TAuthResult;
begin
  Result := False;
  if not TJwtTokenStore.TryLoadPersistedSession then
    Exit;

  LAuthService := TAuthService.Create;
  try
    try
      LAuthResult := LAuthService.Refresh(TJwtTokenStore.GetRefreshToken);
      TJwtTokenStore.SetToken(LAuthResult.AccessToken);
      TJwtTokenStore.SetRefreshToken(LAuthResult.RefreshToken);
      TJwtTokenStore.PersistSession;
      Result := True;
    except
      // Kayitli refresh token gecersiz/suresi dolmus - normal login ekranina dus.
      TJwtTokenStore.Clear;
      TJwtTokenStore.ClearPersistedSession;
      Result := False;
    end;
  finally
    LAuthService.Free;
  end;
end;

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;

  if TryRestorePersistedSession then
  begin
    Application.CreateForm(TFrmMain, FrmMain);
    FrmMain.SetSessionUser(TJwtTokenStore.GetUsername);
  end
  else
    Application.CreateForm(TFrmLogin, FrmLogin);

  Application.Run;
end.
