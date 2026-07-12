unit MainForm;

interface

uses
  Winapi.Windows,
  Winapi.Messages,
  System.SysUtils,
  System.Variants,
  System.Classes,
  Vcl.Graphics,
  Vcl.Controls,
  Vcl.Forms,
  Vcl.Dialogs,
  Vcl.StdCtrls,
  Vcl.ComCtrls,
  Vcl.ExtCtrls;

type
  TFrmMain = class(TForm)
    PnlTop: TPanel;
    LblTitle: TLabel;
    LblWelcome: TLabel;
    LblSession: TLabel;
    BtnSearch: TButton;
    BtnResults: TButton;
    BtnHistory: TButton;
    BtnAdmin: TButton;
    BtnLogout: TButton;
    LblLastQuery: TLabel;
    LblJobStatus: TLabel;
    PrgScan: TProgressBar;
    PollTimer: TTimer;
    procedure BtnSearchClick(Sender: TObject);
    procedure BtnResultsClick(Sender: TObject);
    procedure BtnHistoryClick(Sender: TObject);
    procedure BtnAdminClick(Sender: TObject);
    procedure BtnLogoutClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure PollTimerTimer(Sender: TObject);
  private
    FUsername: string;
    FLastSearchHistoryId: Integer;
    FPollAttempts: Integer;
    procedure RefreshSessionInfo;
    procedure StartJobStatusPolling;
    procedure StopJobStatusPolling(const AFinalCaption: string);
  public
    procedure SetSessionUser(const AUsername: string);
  end;

var
  FrmMain: TFrmMain;

implementation

{$R *.dfm}

uses
  UJwtTokenStore,
  UAuthService,
  USearchService,
  SearchForm,
  ResultsForm,
  HistoryForm,
  AdminForm;

const
  MAX_POLL_ATTEMPTS = 60; // ~3sn * 60 = 3 dakika sonra polling'i guvenlik icin durdur

procedure TFrmMain.BtnSearchClick(Sender: TObject);
begin
  with TFrmSearch.Create(Self) do
  try
    if ShowModal = mrOk then
    begin
      FLastSearchHistoryId := SearchHistoryId;
      LblLastQuery.Caption := 'Son arama: ' + SearchQuery + ' | ID: ' + IntToStr(SearchHistoryId);
      StartJobStatusPolling;
    end;
  finally
    Free;
  end;
end;

procedure TFrmMain.BtnResultsClick(Sender: TObject);
begin
  with TFrmResults.Create(Self) do
  try
    SetDefaultAramaId(FLastSearchHistoryId);
    ShowModal;
  finally
    Free;
  end;
end;

procedure TFrmMain.BtnHistoryClick(Sender: TObject);
begin
  with TFrmHistory.Create(Self) do
  try
    ShowModal;
  finally
    Free;
  end;
end;

procedure TFrmMain.BtnAdminClick(Sender: TObject);
begin
  with TFrmAdmin.Create(Self) do
  try
    ShowModal;
  finally
    Free;
  end;
end;

procedure TFrmMain.BtnLogoutClick(Sender: TObject);
var
  LAuthService: TAuthService;
begin
  LAuthService := TAuthService.Create;
  try
    // Sunucu tarafinda refresh token'i iptal et (en iyi caba - basarisiz olsa da devam et)
    try
      LAuthService.Logout(TJwtTokenStore.GetRefreshToken);
    except
      // Ag/sunucu hatasi cikis islemini engellememeli
    end;
  finally
    LAuthService.Free;
  end;

  TJwtTokenStore.ClearPersistedSession;
  TJwtTokenStore.Clear;
  Application.Terminate;
end;

procedure TFrmMain.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure TFrmMain.RefreshSessionInfo;
begin
  if FUsername = '' then
    LblWelcome.Caption := 'Hos geldiniz'
  else
    LblWelcome.Caption := 'Hos geldiniz, ' + FUsername;

  if TJwtTokenStore.HasToken then
    LblSession.Caption := 'JWT session aktif'
  else
    LblSession.Caption := 'JWT session bulunamadi';
end;

procedure TFrmMain.SetSessionUser(const AUsername: string);
begin
  FUsername := Trim(AUsername);
  FLastSearchHistoryId := 0;
  RefreshSessionInfo;
end;

procedure TFrmMain.StartJobStatusPolling;
begin
  FPollAttempts := 0;
  PrgScan.Style := pbstMarquee;
  PrgScan.Visible := True;
  LblJobStatus.Caption := 'Durum: taraniyor...';
  PollTimer.Enabled := True;
end;

procedure TFrmMain.StopJobStatusPolling(const AFinalCaption: string);
begin
  PollTimer.Enabled := False;
  PrgScan.Visible := False;
  LblJobStatus.Caption := AFinalCaption;
end;

procedure TFrmMain.PollTimerTimer(Sender: TObject);
var
  LSearchService: TSearchService;
  LStatusResult: TScanStatusResult;
begin
  Inc(FPollAttempts);
  if FPollAttempts > MAX_POLL_ATTEMPTS then
  begin
    StopJobStatusPolling('Durum: zaman asimi (sonuclari kontrol edin)');
    Exit;
  end;

  if FLastSearchHistoryId <= 0 then
  begin
    StopJobStatusPolling('');
    Exit;
  end;

  LSearchService := TSearchService.Create;
  try
    try
      LStatusResult := LSearchService.GetScanStatus(FLastSearchHistoryId, TJwtTokenStore.GetToken);
    except
      on E: Exception do
      begin
        // Gecici bir ag hatasinda polling'i durdurma, bir sonraki tick'te tekrar dene
        LblJobStatus.Caption := 'Durum: kontrol edilirken hata (tekrar denenecek)';
        Exit;
      end;
    end;
  finally
    LSearchService.Free;
  end;

  if LStatusResult.Status = 'finished' then
    StopJobStatusPolling('Durum: tarama tamamlandi, sonuclar isleniyor olabilir')
  else if LStatusResult.Status = 'error' then
    StopJobStatusPolling('Durum: hata - ' + LStatusResult.Message)
  else
    LblJobStatus.Caption := 'Durum: taraniyor... (' + LStatusResult.Status + ')';
end;

end.
