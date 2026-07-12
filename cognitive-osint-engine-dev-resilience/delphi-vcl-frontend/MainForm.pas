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
    procedure BtnSearchClick(Sender: TObject);
    procedure BtnResultsClick(Sender: TObject);
    procedure BtnHistoryClick(Sender: TObject);
    procedure BtnAdminClick(Sender: TObject);
    procedure BtnLogoutClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
  private
    FUsername: string;
    FLastSearchHistoryId: Integer;
    procedure RefreshSessionInfo;
  public
    procedure SetSessionUser(const AUsername: string);
  end;

var
  FrmMain: TFrmMain;

implementation

{$R *.dfm}

uses
  UJwtTokenStore,
  SearchForm,
  ResultsForm,
  HistoryForm,
  AdminForm;

procedure TFrmMain.BtnSearchClick(Sender: TObject);
begin
  with TFrmSearch.Create(Self) do
  try
    if ShowModal = mrOk then
    begin
      FLastSearchHistoryId := SearchHistoryId;
      LblLastQuery.Caption := 'Son arama: ' + SearchQuery + ' | ID: ' + IntToStr(SearchHistoryId);
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
begin
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

end.
